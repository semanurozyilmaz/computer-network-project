from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.node import Controller
import re, csv, time, random, statistics, os
import networkx as nx
import matplotlib.pyplot as plt

def cleanup_system():
    os.system("pkill -9 iperf")
    os.system("mn -c > /dev/null 2>&1")

class NetworkTopo(Topo):
    def build(self, bw, delay, loss, queue):
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        s1 = self.addSwitch('s1')

        # Link 1
        self.addLink(h1, s1, cls=TCLink, bw=100, delay='1ms', loss=0)

        # Link 2
        self.addLink(s1, h2, cls=TCLink,
                     bw=bw, 
                     delay=f"{delay}ms",
                     loss=loss, 
                     max_queue_size=queue, 
                     use_htb=True)
        
def visualize_topology():
    G = nx.Graph()
    G.add_edges_from([('h1', 's1'), ('s1', 'h2')])
    pos = {'h1': (0, 0), 's1': (1, 0), 'h2': (2, 0)}
    plt.figure(figsize=(6, 2))
    nx.draw(G, pos, with_labels=True, node_size=2000)
    plt.title("Mininet Topology")
    plt.show()

def run_experiment(bw, delay, loss, queue):
    cleanup_system()

    topo = NetworkTopo(bw, delay, loss, queue)
    net = Mininet(topo=topo, link=TCLink, controller=Controller, autoSetMacs=True)

    try:
        net.start()
        h1 = net.get('h1')
        h2 = net.get('h2')

        # ARKA PLAN TRAFİĞİ (IPERF)
        h2.cmd("iperf -u -s -p 5001 > iperf_server_report.txt &")
        time.sleep(0.5)
        
        h1.cmd(f"iperf -u -c 10.0.0.2 -p 5001 -b {bw}M -t 10 &")

        time.sleep(2) 

        # PING ÖLÇÜMÜ (Trafik Altında)
        ping_output = h1.cmd("ping -c 30 -i 0.1 10.0.0.2")
        time.sleep(5) 

        rtts = [float(r) for r in re.findall(r'time=([\d\.]+) ms', ping_output)]
        rtt_avg = statistics.mean(rtts) if rtts else 0.0
        
        jitter = statistics.stdev(rtts) if len(rtts) > 1 else 0.0
        
        h2.cmd("pkill -9 iperf")
        report = open("iperf_server_report.txt","r").read()

        loss_match = re.findall(r'\((\d+\.?\d*)%\)', report)
        packet_loss_ratio = float(loss_match[-1]) if loss_match else 0.0

        tput_match = re.findall(r'(\d+\.?\d*)\s+Mbits/sec', report)
        throughput = float(tput_match[-1]) if tput_match else 0.0

        time.sleep(2)
        h2.cmd("pkill -9 iperf")
        return {
            "bw": bw, "delay": delay, "loss": loss, "queue": queue,
            "packet_loss_ratio": packet_loss_ratio,
            "rtt": round(rtt_avg,3), "jitter": round(jitter,3), "throughput": throughput
        }

    except Exception as e:
        print(f"Hata oluştu: {e}")
        return None
    finally:
        net.stop()
        cleanup_system()

def main():

    visualize_topology()
    
    num_samples = 576
    filename = "simulation3.csv"

    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "bw", "delay", "loss", "queue",
            "packet_loss_ratio", "rtt", "jitter", "throughput"
        ])

        for i in range(num_samples):
            bw = round(random.uniform(5,30),2)
            delay = round(random.uniform(5,80),2)
            loss = round(random.uniform(0,10),2)
            queue = random.randint(20,250)

            print(f"[{i+1}/{num_samples}]")
            result = run_experiment(bw, delay, loss, queue)

            if result:
                writer.writerow(result.values())
                f.flush()
            time.sleep(0.5)
    print(f"\nİşlem tamamlandı. {filename} oluşturuldu.")
            
main()