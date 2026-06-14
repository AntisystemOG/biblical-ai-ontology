## Degater PLC Tool BST33 and 35 — Showcase Metrics

### What It Is
Desktop diagnostics application for Allen-Bradley Micro870 PLCs on plant-floor lines BST33 and BST35, built with AI-assisted development.

### Capabilities (Management-Friendly)
- Real-time PLC I/O monitoring with live LED status indicators
- Timeline recording & playback for fault sequence analysis
- Fault logging with timestamps for troubleshooting history
- Output forcing/testing for safe commissioning
- Tag browser & monitor from CSV mapping
- Motion data (PTO axis position / velocity)
- Expansion module auto-discovery (slots 2–8)
- System diagnostics: Run/Program/Faulted mode, fault flags, module health

### Cost Reality
| | AI-Assisted | Commercial Equivalent |
|---|---|---|
| Development cost | ~$20/month AI subscription | $5,000–$15,000+ vendor/custom |
| Annual software | ~$240/year | $1,000–$3,000/seat/year (RSLogix/FactoryTalk) |
| Customization | Unlimited, tailored to exact line | Limited to vendor roadmap |
| Time to value | Days–weeks | Weeks–months procurement |

### Technical Stack
- PySide6 GUI, pycomm3 Ethernet-IP/CIP protocol
- Built iteratively with AI pair-programming
- Outputs single Windows executable (PyInstaller)
- Runs entirely on local plant-floor laptops — no cloud dependency

### Business Outcomes for Intralox
1. **Reduced downtime** — On-site diagnosis without waiting for vendor support
2. **Faster commissioning** — New lines come online sooner with purpose-built tools
3. **Knowledge retention** — Replayable fault timelines reduce tribal knowledge dependency
4. **No vendor lock-in** — Open Python stack, not tied to Rockwell licensing
5. **Scalable** — Same AI-assisted pattern works for other plant systems