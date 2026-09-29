# Demo walkthrough

1. Open the dashboard at `http://localhost:5173`.
2. Select **Simulate Brute Force**.
3. The demo emits 35–50 failed login events from one IP.
4. On the twentieth event, the detection agent creates a `BRUTE_FORCE` incident.
5. Threat hunting returns its related timeline; risk assessment scores it `HIGH`; the response agent simulates `BLOCK_IP`.
6. Open the incident row to inspect its evidence, factors, action record, report, and agent decisions.

The other simulator controls demonstrate port scanning, critical container activity, and benign traffic. All response actions are allowlisted and operate in simulation mode by default.

