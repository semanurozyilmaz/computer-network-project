from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
import re
import csv
import time
import random
import statistics

class NetworkTopo(Topo):
    def build(self, bw, delay, loss, queue):
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')

        self.addLink(
            h1, h2,
            cls=TCLink,
            bw=bw,
            delay=f"{delay}ms",
            loss=loss,
            max_queue_size=queue,
            use_htb=True
        )


def run_experiment(bw, delay, loss, queue):
    topo = NetworkTopo(bw, delay, loss, queue)
    net = Mininet(topo=topo, link=TCLink)
    net.start()

    h1 = net.get('h1')
    h2 = net.get('h2')

    # PING
    ping_output = h1.cmd("ping -c 5 -W 1 10.0.0.2")

    loss_match = re.search(r'(\d+)% packet loss', ping_output)
    packet_loss_ratio = int(loss_match.group(1)) if loss_match else 100

    rtts = re.findall(r'time=([\d\.]+) ms', ping_output)
    rtts = [float(r) for r in rtts]
    rtt_avg = statistics.mean(rtts) if rtts else None
    jitter = statistics.stdev(rtts) if len(rtts) > 1 else 0.0

    # IPERF
    h2.cmd("pkill iperf")
    time.sleep(0.2)
    h2.cmd("iperf -u -s -p 5001 &")
    time.sleep(0.5)

    iperf_cmd = f"timeout 4 iperf -u -c 10.0.0.2 -p 5001 -b {bw}M -t 3"
    iperf_output = h1.cmd(iperf_cmd)

    h2.cmd("pkill iperf")

    tput = re.search(r'([\d\.]+)\s*Mbits/sec', iperf_output)
    throughput = float(tput.group(1)) if tput else 0.0

    net.stop()

    return {
        "bw": bw,
        "delay": delay,
        "loss": loss,
        "queue": queue,
        "packet_loss_ratio": packet_loss_ratio,
        "rtt": rtt_avg,
        "jitter": jitter,
        "throughput": throughput
    }

def main():
    # Test ranges
    bw_values = [5, 10, 20, 50]
    loss_values = [0, 1, 2, 5]
    queue_values = [50, 100, 200]

    filename = "network_dataset.csv"
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "bw", "delay", "loss", "queue",
            "packet_loss_ratio", "rtt", "jitter", "throughput"
        ])

        for _ in range(576):  # samples
            bw = random.choice(bw_values)
            delay = random.uniform(5,50)
            loss = random.choice(loss_values)
            queue = random.choice(queue_values)

            result = run_experiment(bw, delay, loss, queue)
            writer.writerow(result.values())

    print("Dataset generated:", filename)


main()