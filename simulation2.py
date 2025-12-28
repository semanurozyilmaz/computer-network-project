from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.node import Controller
import re, csv, time, random, statistics
import networkx as nx
import matplotlib.pyplot as plt

class NetworkTopo(Topo):
    def build(self, bw, delay, loss, queue):
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        s1 = self.addSwitch('s1')

        self.addLink(h1, s1, cls=TCLink, bw=100, delay='1ms', loss=0)

        self.addLink(s1, h2, cls=TCLink,
                     bw=bw,
                     delay=f"{delay}ms",
                     loss=loss,
                     max_queue_size=queue,
                     use_htb=True)

def visualize_topology():
    G = nx.Graph()
    G.add_edges_from([('h1', 'h2')])
    pos = {'h1': (0, 0), 'h2': (1, 0)}
    plt.figure(figsize=(6, 2))
    nx.draw(G, pos, with_labels=True, node_size=2000)
    plt.title("Mininet Topology")
    plt.show()

def run_experiment(bw, delay, loss, queue):
    topo = NetworkTopo(bw, delay, loss, queue)
    net = Mininet(topo=topo, link=TCLink, controller=Controller, autoSetMacs=True)
    
    try:
        net.start()
        h1 = net.get('h1')
        h2 = net.get('h2')

        h2.cmd("pkill -9 iperf")
        h2.cmd("iperf -u -s -p 5001 &")

        time.sleep(0.5)
        h1.cmd(f"iperf -u -c 10.0.0.2 -p 5001 -b {bw}M -t 10 &")
        time.sleep(2)

        ping_output = h1.cmd("ping -c 10 -i 0.2 10.0.0.2")


        loss_match = re.search(r'(\d+)% packet loss', ping_output)
        packet_loss_ratio = int(loss_match.group(1)) if loss_match else 100


        rtts = [float(r) for r in re.findall(r'time=([\d\.]+) ms', ping_output)]
        rtt_avg = statistics.mean(rtts) if rtts else None

        jitter = statistics.stdev(rtts) if len(rtts) > 1 else 0.0

        time.sleep(2)
        h2.cmd("pkill -9 iperf")

        return {
            "bw": bw, "delay": delay, "loss": loss, "queue": queue,
            "packet_loss_ratio": packet_loss_ratio,
            "rtt": rtt_avg, "jitter": jitter, "throughput": bw * (1 - (packet_loss_ratio/100)) 
        }

    finally:
        net.stop()

def main():
    # Test ranges
    bw_values = [5, 10, 20, 50]
    loss_values = [0, 1, 2, 5]
    queue_values = [50, 100, 200]

    visualize_topology()
    num_samples = 576

    filename = "simulation2.csv"
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "bw", "delay", "loss", "queue",
            "packet_loss_ratio", "rtt", "jitter", "throughput"
        ])

        for i in range(num_samples = 576): 
            bw = random.choice(bw_values)
            delay = random.uniform(5,50)
            loss = random.choice(loss_values)
            queue = random.choice(queue_values)

            print(f"[{i+1}/{num_samples}]")
            result = run_experiment(bw, delay, loss, queue)
            writer.writerow(result.values())
            f.flush()

    print("Dataset generated:", filename)


main()