import os

def generate_fattree6_rules():
    # k = 6
    num_pods = 6
    num_hosts_per_edge = 3
    num_edge_switches_per_pod = 3
    num_agg_switches_per_pod = 3
    num_core_switches = 9

    # Create rules directory if it doesn't exist
    if not os.path.exists("rules"):
        os.makedirs("rules")

    # 1. Edge switches (s1 - s18)
    for pod in range(num_pods):
        for edge in range(num_edge_switches_per_pod):
            switch_num = pod * num_edge_switches_per_pod + edge + 1
            with open(f"rules/s{switch_num}-commands.txt", "w") as f:
                # Downward to hosts (Ports 1, 2, 3)
                for host in range(num_hosts_per_edge):
                    ip = f"10.{pod}.{edge}.{host + 1}/32"
                    mac = f"00:00:0a:00:{pod:02x}:{edge:02x}" # Simplified MAC
                    out_port = host + 1
                    for in_port in range(1, 7):
                        if in_port != out_port:
                            f.write(f"table_add MyIngress.ipv4_lpm MyIngress.ipv4_forward {ip} {in_port} => {mac} {out_port}\n")

                # Upward to Aggregation (Ports 4, 5, 6)
                # For simplicity, route all non-local traffic to agg switches
                # To avoid duplicate keys, we use more specific routes or a default behavior.
                # In FatTree, we can route based on the destination pod/edge.
                for dest_pod in range(num_pods):
                    for dest_edge in range(num_edge_switches_per_pod):
                        if dest_pod != pod or dest_edge != edge:
                            ip_prefix = f"10.{dest_pod}.{dest_edge}.0/24"
                            # Distribute traffic among the 3 agg switches
                            agg_idx = (dest_pod + dest_edge) % 3
                            out_port = 4 + agg_idx
                            mac = f"00:00:0a:00:{pod:02x}:{num_edge_switches_per_pod + agg_idx:02x}"
                            for in_port in range(1, 4): # Only from hosts
                                f.write(f"table_add MyIngress.ipv4_lpm MyIngress.ipv4_forward {ip_prefix} {in_port} => {mac} {out_port}\n")

    # 2. Aggregation switches (s19 - s36)
    for pod in range(num_pods):
        for agg in range(num_agg_switches_per_pod):
            switch_num = num_pods * num_edge_switches_per_pod + pod * num_agg_switches_per_pod + agg + 1
            with open(f"rules/s{switch_num}-commands.txt", "w") as f:
                # Downward to Edge (Ports 4, 5, 6)
                for edge in range(num_edge_switches_per_pod):
                    ip_prefix = f"10.{pod}.{edge}.0/24"
                    mac = f"00:00:0a:00:{pod:02x}:{edge:02x}"
                    out_port = 4 + edge
                    for in_port in range(1, 4): # From Core
                        f.write(f"table_add MyIngress.ipv4_lpm MyIngress.ipv4_forward {ip_prefix} {in_port} => {mac} {out_port}\n")

                # Upward to Core (Ports 1, 2, 3)
                for dest_pod in range(num_pods):
                    if dest_pod != pod:
                        ip_prefix = f"10.{dest_pod}.0.0/16"
                        # Use a specific core switch port (1, 2, or 3)
                        out_port = (dest_pod % 3) + 1
                        mac = f"00:00:0a:01:00:00" # Simplified MAC for Core
                        for in_port in range(4, 7): # From Edge
                            f.write(f"table_add MyIngress.ipv4_lpm MyIngress.ipv4_forward {ip_prefix} {in_port} => {mac} {out_port}\n")

    # 3. Core switches (s37 - s45)
    for core in range(num_core_switches):
        switch_num = num_pods * num_edge_switches_per_pod + num_pods * num_agg_switches_per_pod + core + 1
        with open(f"rules/s{switch_num}-commands.txt", "w") as f:
            for dest_pod in range(num_pods):
                ip_prefix = f"10.{dest_pod}.0.0/16"
                mac = f"00:00:0a:00:{dest_pod:02x}:00"
                out_port = dest_pod + 1 # Each core connects to one agg switch per pod
                for in_port in range(1, 7):
                    if in_port != out_port:
                        f.write(f"table_add MyIngress.ipv4_lpm MyIngress.ipv4_forward {ip_prefix} {in_port} => {mac} {out_port}\n")

def append_p4prime_rules():
    # Generate a list of prime numbers for switch IDs
    primes = []
    num = 2
    while len(primes) < 45:
        is_prime = True
        for i in range(2, int(num**0.5) + 1):
            if num % i == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(num)
        num += 1

    num_switches = 45
    for i in range(1, num_switches + 1):
        prime = primes[i-1]
        default_rules = [
            f"\n// Phase 1: consistency verification",
            f"table_set_default MyEgress.tbl_prime prime_multiply {prime}",
            f"\n// Phase 2: inconsistency location",
            f"table_set_default MyEgress.swtrace add_swtrace {i}\n"
        ]
        with open(f"rules/s{i}-commands.txt", "a") as f:
            f.write("\n".join(default_rules))

if __name__ == "__main__":
    generate_fattree6_rules()
    append_p4prime_rules()
    print("Regenerated all rules with correct port mapping and device-specific configs.")
