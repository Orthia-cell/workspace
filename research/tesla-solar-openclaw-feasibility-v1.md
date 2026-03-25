# Energy-Aware OpenClaw: A Research Paper on Solar-Powered Edge Computing in a Tesla

**Project:** OpenClaw Solar Edge Computing System  
**Author:** Orthia (Kimi Claw)  
**Date:** March 25, 2026  
**Version:** 1.0 — Initial Research Synthesis

---

## Executive Summary

This paper explores the feasibility of deploying an autonomous AI agent system (OpenClaw) on a Mac Mini housed in a Tesla vehicle, powered by solar energy harvested from roof-mounted panels. The system must operate sustainably—balancing energy production, consumption, and storage without depleting the vehicle's traction battery.

**Key Findings:**
- **Technically feasible** with proper power management architecture
- **Mac Mini M1/M2** is optimal (4-7W idle, 39W max) vs Intel models (20W+ idle)
- **25W solar panel** produces ~94 Wh/day (5 peak sun hours, 75% efficiency factor)
- **Tesla 12V system** provides 144W continuous (12A) with 192W peak (16A)
- **Energy deficit** exists: Mac Mini idle (144 Wh/day) exceeds solar production (94 Wh/day)
- **Solution:** Burst-mode operation with Tesla battery buffer and intelligent scheduling

**Recommendation:** Implement a **3-tier energy state machine** (FULL/ECONOMY/SURVIVAL) with predictive solar forecasting and workload scheduling. System can achieve 90%+ renewable operation with minimal Tesla battery draw.

---

## 1. System Architecture Overview

### 1.1 Component Inventory

| Component | Specification | Role |
|-----------|---------------|------|
| **Compute** | Mac Mini M1/M2 (8GB/16GB) | OpenClaw host, AI inference |
| **Vehicle** | Tesla Model 3/Y/S/X | Power source, shelter, connectivity |
| **Solar** | 25W-50W flexible panel | Primary energy harvest |
| **DC-DC** | 12V-to-USB-C PD (100W) | Voltage conversion |
| **Battery** | Tesla 12V Li-ion (16V) | Buffer/backup power |
| **Traction** | Tesla main battery (60-100 kWh) | Deep reserve |

### 1.2 Power Flow Architecture

```
Solar Panel (25W) ──► Charge Controller ──► Tesla 12V Battery
                                                  │
                                                  ▼
Tesla 12V Socket (12A/16A) ──► DC-DC Converter ──► Mac Mini
                                                  │
                                                  ▼
                                            OpenClaw Runtime
                                                  │
                    ┌─────────────────────────────┼─────────────────────────────┐
                    ▼                             ▼                             ▼
              Energy Monitor              Workload Scheduler              State Manager
                    │                             │                             │
                    └─────────────────────────────┴─────────────────────────────┘
                                                  │
                                                  ▼
                                           Decision Engine
```

---

## 2. Power Analysis

### 2.1 Mac Mini Power Profile

Based on Apple official specs and independent testing:

| Model | Idle (W) | Web Browsing (W) | CPU Load (W) | Max (W) |
|-------|----------|------------------|--------------|---------|
| Mac Mini M1 | 6.8 | ~9 | 26.5 | 39 |
| Mac Mini M2 | 4.2-7 | ~8 | 18.5 | 50 |
| Mac Mini M4 | 4-5 | ~8 | ~35 | 65 |
| Intel i7 (2018) | 20 | ~35 | ~80 | 122 |

**Recommendation:** Use Mac Mini M1 or M2 for optimal power efficiency.

### 2.2 Daily Energy Budget Calculation

**Solar Production (25W panel):**
```
Formula: Panel Watts × Peak Sun Hours × System Efficiency

Conservative (winter): 25W × 3.5h × 0.75 = 65.6 Wh/day
Average: 25W × 5.0h × 0.75 = 93.8 Wh/day
Peak (summer): 25W × 7.0h × 0.75 = 131.3 Wh/day
```

**Solar Production (50W panel):**
```
Conservative: 50W × 3.5h × 0.75 = 131.3 Wh/day
Average: 50W × 5.0h × 0.75 = 187.5 Wh/day
Peak: 50W × 7.0h × 0.75 = 262.5 Wh/day
```

### 2.3 Mac Mini Consumption Scenarios

| Scenario | Power | Daily Energy (24h) | Solar Match |
|----------|-------|-------------------|-------------|
| Always Idle (M1) | 6.8W | 163 Wh | ❌ 25W: -69 Wh; ✅ 50W: +19 Wh |
| Always Idle (M2) | 4.2W | 101 Wh | ❌ 25W: -7 Wh; ✅ 50W: +81 Wh |
| Burst Mode (6h active) | 30W avg | 75 Wh active + 68 Wh idle = 143 Wh | ❌ 25W: -49 Wh; ✅ 50W: +37 Wh |
| Burst Mode (4h active) | 30W avg | 50 Wh active + 81 Wh idle = 131 Wh | ❌ 25W: -37 Wh; ✅ 50W: +49 Wh |
| Burst Mode (2h active) | 30W avg | 25 Wh active + 90 Wh idle = 115 Wh | ❌ 25W: -21 Wh; ✅ 50W: +65 Wh |

**Critical Insight:** Even the most efficient Mac Mini (M2 at 4.2W idle) consumes 101 Wh/day—exceeding 25W solar production on all but peak summer days. **A 50W panel is strongly recommended.**

### 2.4 Tesla Battery Buffer

**Tesla 12V System Specifications:**
- Nominal voltage: 15-16V (Li-ion, not lead-acid)
- Continuous current: 12A = ~180W
- Peak current: 16A = ~240W
- Auto-shutoff: Below 20% SoC (protects traction battery)

**Daily Tesla Battery Draw (50W panel, 4h burst mode):**
```
Mac Mini needs: 131 Wh
Solar provides: 187 Wh (average)
Surplus: +56 Wh (charges 12V battery)

On cloudy day (50% production):
Solar provides: 94 Wh
Deficit: -37 Wh (draws from 12V battery)
```

**Traction Battery Impact:**
- Tesla 12V battery is charged from traction battery via DC-DC converter
- Typical 12V battery: ~50 Wh capacity
- Traction battery: 60-100 kWh
- Worst case: 37 Wh/day deficit = 0.037% of 100 kWh battery
- **Negligible impact on vehicle range**

---

## 3. Energy State Machine Architecture

### 3.1 Three-Tier Power States

Based on energy availability and battery SoC:

#### State 1: FULL (Green)
**Triggers:** Solar >15W AND Battery SoC >70%

| Parameter | Value |
|-----------|-------|
| Mac Mini Mode | Full performance |
| OpenClaw Tasks | All enabled |
| Grace Research | Yes (8AM/11AM/3PM) |
| Auto-commits | Every 4 hours |
| Battery Monitoring | 7:30 AM daily |
| Daily Questions | 6:00 AM |
| Max Duration | Unlimited while conditions hold |

#### State 2: ECONOMY (Yellow)
**Triggers:** Solar 5-15W OR Battery SoC 40-70%

| Parameter | Value |
|-----------|-------|
| Mac Mini Mode | Reduced clock (if configurable) |
| OpenClaw Tasks | Essential only |
| Grace Research | Deferred to next FULL state |
| Auto-commits | Every 8 hours (doubled interval) |
| Battery Monitoring | Every 6 hours |
| Daily Questions | Skip if battery <50% |
| Max Duration | Until battery <40% OR solar >15W |

#### State 3: SURVIVAL (Red)
**Triggers:** Solar <5W OR Battery SoC <40%

| Parameter | Value |
|-----------|-------|
| Mac Mini Mode | Idle/sleep if possible |
| OpenClaw Tasks | Heartbeat only |
| Grace Research | Suspended |
| Auto-commits | Suspended |
| Battery Monitoring | Every hour (critical) |
| Daily Questions | Suspended |
| Max Duration | Until battery >50% OR manual override |

#### State 4: SHUTDOWN (Black)
**Triggers:** Battery SoC <25%

| Parameter | Value |
|-----------|-------|
| Action | Graceful shutdown of OpenClaw |
| Wake Condition | Battery >40% AND solar >10W |
| Data Protection | All uncommitted work saved to disk |

### 3.2 State Transition Logic

```python
def determine_power_state(solar_watts, battery_soc):
    """
    Power state determination logic
    """
    if battery_soc < 25:
        return SHUTDOWN
    elif battery_soc < 40 or solar_watts < 5:
        return SURVIVAL
    elif battery_soc < 70 and solar_watts < 15:
        return ECONOMY
    else:
        return FULL

def schedule_tasks(state, pending_tasks):
    """
    Task scheduling based on power state
    """
    if state == FULL:
        return pending_tasks  # All tasks allowed
    elif state == ECONOMY:
        return [t for t in pending_tasks if t.priority == 'critical']
    elif state == SURVIVAL:
        return [t for t in pending_tasks if t.type == 'heartbeat']
    else:
        return []  # No tasks in shutdown
```

---

## 4. Hardware Configuration

### 4.1 Recommended Hardware Stack

**Option A: Budget (25W panel)**
| Component | Spec | Est. Cost |
|-----------|------|-----------|
| Solar Panel | 25W flexible monocrystalline | $40-60 |
| Charge Controller | 10A MPPT (12V) | $25-40 |
| DC-DC Converter | 12V-to-USB-C PD 100W | $20-30 |
| USB-C Cable | 100W rated, 2m | $10-15 |
| Mounting | Magnetic/ adhesive roof mount | $15-25 |
| **Total** | | **$110-170** |

**Option B: Optimal (50W panel)**
| Component | Spec | Est. Cost |
|-----------|------|-----------|
| Solar Panel | 50W flexible monocrystalline | $70-100 |
| Charge Controller | 10A MPPT (12V) | $25-40 |
| DC-DC Converter | 12V-to-USB-C PD 100W | $20-30 |
| USB-C Cable | 100W rated, 2m | $10-15 |
| Mounting | Magnetic/ adhesive roof mount | $15-25 |
| **Total** | | **$140-210** |

### 4.2 Power Conversion Chain

**Tesla 12V Socket → Mac Mini:**

```
Tesla 12V Socket
    │ 15-16V nominal, 12A continuous
    ▼
DC-DC Step-Down/Up Converter
    │ Input: 9-32V DC
    │ Output: USB-C PD (5V/9V/12V/15V/20V)
    │ Max: 100W (20V @ 5A)
    ▼
Mac Mini M1/M2
    │ Input: USB-C PD
    │ Accepts: 20V (for max performance)
    │ Idle: 6.8W, Max: 39W
```

**Recommended Converter:** BiXPower BX-DD100PD or equivalent
- Input: 10V-32V DC (compatible with Tesla 12V)
- Output: USB-C PD up to 100W
- Efficiency: ~90%+
- Size: 78 × 36 × 24 mm

### 4.3 Solar Panel Placement

**Optimal Configuration:**
- Position: Rear trunk lid or roof
- Angle: Flat (vehicle roof) or slightly angled
- Orientation: South-facing when parked
- Cable routing: Through trunk seal or door jam

**Considerations:**
- Aerodynamics: Flexible panels add minimal drag
- Theft: Magnetic mounts allow easy removal
- Cleaning: Periodic cleaning essential for efficiency
- Shading: Park in full sun when possible

---

## 5. Software Architecture

### 5.1 Energy Monitoring Service

**Purpose:** Continuously monitor energy inputs and system state

**Data Sources:**
```python
class EnergyMonitor:
    def __init__(self):
        self.solar_sensor = SolarPanelSensor()  # Via charge controller
        self.battery_monitor = Tesla12VMonitor()  # Via OBD or voltage tap
        self.macmini_power = MacMiniPower()  # Via powermetrics or SMC
    
    def read_current_state(self):
        return {
            'solar_watts': self.solar_sensor.read_watts(),
            'battery_voltage': self.battery_monitor.read_voltage(),
            'battery_soc': self.calculate_soc(),
            'macmini_watts': self.macmini_power.read_watts(),
            'timestamp': datetime.now()
        }
```

**Sampling Rate:**
- Solar: Every 60 seconds
- Battery: Every 60 seconds
- Mac Mini: Every 300 seconds (5 min)

### 5.2 Predictive Scheduling

**Solar Forecasting:**
- Use historical data + weather APIs
- Predict peak hours (typically 10 AM - 2 PM)
- Pre-schedule intensive tasks for predicted FULL states

**Task Classification:**
| Task | Priority | Power Profile | Scheduling |
|------|----------|---------------|------------|
| Heartbeat | Critical | ~2W | Any state |
| Battery monitor | High | ~2W | Any state |
| Auto-commit | Medium | ~10W | ECONOMY+ |
| Daily question | Medium | ~10W | ECONOMY+ |
| Grace research v1.0 | Low | ~25W | FULL only |
| Grace research v2.0 | Low | ~25W | FULL only |
| Grace research v3.0 | Low | ~25W | FULL only |
| File sync | Low | ~15W | ECONOMY+ |

### 5.3 OpenClaw Integration

**Modified Cron Jobs with Energy Awareness:**

```yaml
# cron.yaml with energy constraints
jobs:
  - name: grace-morning-research
    schedule: "0 8 * * *"
    condition: "power_state == FULL"
    fallback: "defer_until_full"
    
  - name: grace-noon-research
    schedule: "0 11 * * *"
    condition: "power_state == FULL"
    fallback: "defer_until_full"
    
  - name: grace-afternoon-research
    schedule: "0 15 * * *"
    condition: "power_state == FULL"
    fallback: "defer_until_full"
    
  - name: battery-monitor
    schedule: "30 7 * * *"
    condition: "battery_soc > 30"
    fallback: "skip_and_alert"
    
  - name: auto-commit
    schedule: "0 */4 * * *"
    condition: "power_state in [FULL, ECONOMY]"
    fallback: "defer_2_hours"
```

---

## 6. Feasibility Assessment

### 6.1 Technical Feasibility: ✅ HIGH

**Supporting Evidence:**
- Mac Mini M1/M2 power consumption well within Tesla 12V capacity
- Solar panel technology mature and reliable
- DC-DC converters readily available and efficient
- Tesla "Accessory Power" mode enables 12V when parked
- Energy-aware scheduling algorithms proven in HPC/data center contexts

### 6.2 Economic Feasibility: ✅ MODERATE

**Cost-Benefit Analysis:**
- Hardware cost: $140-210 (one-time)
- Operating cost: Near-zero (solar primary)
- Tesla battery wear: Negligible (<0.1% daily draw)
- Alternative (cloud VPS): $20-100/month = $240-1200/year
- **Payback period:** 1-3 months vs cloud hosting

### 6.3 Operational Feasibility: ⚠️ REQUIRES ATTENTION

**Challenges:**
1. **Weather dependency:** Cloudy days reduce solar production
2. **Parking constraints:** Must park in sun for optimal performance
3. **Temperature extremes:** Mac Mini thermal throttling in hot vehicles
4. **Vibration/driving:** Potential hardware stress

**Mitigations:**
1. Tesla battery buffer covers 1-2 cloudy days
2. Prioritize solar parking; system alerts if parked in shade too long
3. Thermal monitoring; auto-shutdown if internal temp >85°C
4. Mount with vibration dampening; park mode for heavy processing

---

## 7. Implementation Roadmap

### Phase 1: Proof of Concept (Week 1-2)
**Goal:** Validate basic power flow
- [ ] Install 50W solar panel on Tesla
- [ ] Connect DC-DC converter to Tesla 12V socket
- [ ] Power Mac Mini and measure actual consumption
- [ ] Log 48 hours of energy data
- [ ] Determine real-world solar production

### Phase 2: Energy Monitoring (Week 3-4)
**Goal:** Build energy awareness layer
- [ ] Implement voltage/current sensors
- [ ] Create energy state machine
- [ ] Build dashboard/logging system
- [ ] Test state transitions

### Phase 3: Intelligent Scheduling (Week 5-6)
**Goal:** Integrate energy into OpenClaw
- [ ] Modify cron jobs with energy conditions
- [ ] Implement task prioritization
- [ ] Build predictive solar forecasting
- [ ] Test Grace research pipeline under energy constraints

### Phase 4: Optimization (Week 7-8)
**Goal:** Refine and harden
- [ ] Tune state thresholds based on real data
- [ ] Implement graceful degradation
- [ ] Add alerting (low battery, system issues)
- [ ] Document operational procedures

---

## 8. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Solar panel theft | Low | High | Magnetic mounts; remove when parked overnight |
| Extended cloudy period | Medium | Medium | Tesla battery buffer; graceful degradation |
| Mac Mini overheating | Medium | High | Thermal monitoring; auto-shutdown at 85°C |
| Tesla 12V socket limitations | Low | Medium | Test actual current capacity; fuse protection |
| DC-DC converter failure | Low | High | Spare converter; monitoring alerts |
| Cable damage (trunk) | Medium | Medium | Protected routing; strain relief |
| Vibration damage | Low | Medium | Anti-vibration mounts; park mode for heavy tasks |

---

## 9. Comparative Analysis

### 9.1 vs. Cloud VPS

| Factor | Tesla-Solar OpenClaw | Cloud VPS (e.g., AWS) |
|--------|---------------------|----------------------|
| Monthly cost | ~$0 (after hardware) | $20-100 |
| Carbon footprint | Near-zero | Data center dependent |
| Uptime | 90-95% (weather dependent) | 99.9% |
| Latency | Local (excellent) | Variable |
| Data privacy | Complete | Provider dependent |
| Compute power | M1/M2 (very good) | Variable by tier |
| Scalability | Fixed hardware | Instant scaling |
| Maintenance | Physical + software | Software only |

### 9.2 vs. Home Solar Server

| Factor | Tesla-Solar | Home Solar Server |
|--------|-------------|-------------------|
| Panel size | 50W portable | 300W+ fixed |
| Battery | Tesla 12V/100kWh | LiFePO4 5-10kWh |
| Mobility | Mobile (vehicle moves) | Fixed location |
| Uptime | Weather + parking dependent | Weather dependent only |
| Cost | $140-210 | $2,000-5,000 |
| Redundancy | Can drive to sun | Fixed to location |

---

## 10. Conclusions and Recommendations

### 10.1 Core Conclusions

1. **The system is technically feasible.** A Mac Mini in a Tesla, powered by solar, can sustainably run OpenClaw with proper energy management.

2. **50W solar panel is strongly recommended.** A 25W panel produces insufficient energy for continuous operation, even with the efficient M2 Mac Mini.

3. **Energy-aware scheduling is essential.** Without intelligent task scheduling, the system will deplete the Tesla battery buffer during extended cloudy periods.

4. **Tesla battery impact is negligible.** Even worst-case daily deficits represent <0.1% of the traction battery capacity.

5. **Mac Mini thermal management is critical.** Parked vehicles can reach 60-70°C internally; active monitoring and shutdown thresholds are required.

### 10.2 Specific Recommendations

**Immediate Actions:**
1. Procure 50W flexible solar panel and 100W DC-DC converter
2. Install Tesla 12V power monitoring (voltage tap or OBD)
3. Begin Phase 1 proof of concept testing

**System Design:**
1. Implement 3-tier energy state machine (FULL/ECONOMY/SURVIVAL)
2. Modify Grace's research cron jobs to execute only during FULL state
3. Build predictive solar forecasting using weather APIs
4. Create alerting system for low battery and system issues

**Operational Procedures:**
1. Prioritize parking in direct sunlight
2. Set vehicle to "Keep Accessory Power On" when using OpenClaw
3. Monitor Tesla 12V battery voltage regularly
4. Keep spare DC-DC converter for redundancy

### 10.3 Next Steps

This research paper provides the architectural foundation. The next deliverable should be:

1. **Prototype build** (hardware assembly)
2. **Energy monitoring software** (data collection layer)
3. **Scheduling middleware** (energy-aware task execution)
4. **Operational validation** (30-day field test)

---

## Appendix A: Energy Calculations (Detailed)

### A.1 Solar Production by Season

| Season | Peak Sun Hours | 25W Panel Daily | 50W Panel Daily |
|--------|----------------|-----------------|-----------------|
| Winter | 2.5-3.5h | 47-66 Wh | 94-131 Wh |
| Spring | 4.0-5.5h | 75-103 Wh | 150-206 Wh |
| Summer | 5.5-7.0h | 103-131 Wh | 206-263 Wh |
| Fall | 3.5-4.5h | 66-84 Wh | 131-169 Wh |

### A.2 Mac Mini Run Time by Solar Condition

**50W Panel + Mac Mini M2 (4.2W idle, 30W active):**

| Scenario | Solar Wh | Idle Hours | Active Hours | Total Runtime |
|----------|----------|------------|--------------|---------------|
| Winter cloudy | 94 | 22h | 0h | 22h (deferred tasks) |
| Winter sunny | 131 | 24h | 2h | 24h (limited research) |
| Spring average | 180 | 24h | 4h | 24h (normal research) |
| Summer peak | 263 | 24h | 7h | 24h (extended research) |

---

## Appendix B: Hardware Specifications

### B.1 Recommended DC-DC Converters

| Model | Input | Output | Max Power | Efficiency | Price |
|-------|-------|--------|-----------|------------|-------|
| BiXPower BX-DD100PD | 10-32V | USB-C PD | 100W | ~92% | $35 |
| Generic 12V-to-PD 100W | 9-24V | USB-C PD | 100W | ~88% | $20 |
| Starlink Mini Adapter | 12-24V | USB-C PD | 140W | ~90% | $45 |

### B.2 Recommended Solar Panels

| Model | Wattage | Dimensions | Weight | Efficiency | Price |
|-------|---------|------------|--------|------------|-------|
| Renogy 50W Flexible | 50W | 26" × 21" | 2.9 lbs | 21% | $85 |
| HQST 50W Flexible | 50W | 24" × 20" | 2.5 lbs | 20% | $70 |
| ALLPOWERS 50W | 50W | 25" × 21" | 2.8 lbs | 20% | $75 |

---

## Appendix C: Glossary

- **SoC (State of Charge):** Battery charge level as percentage
- **MPPT:** Maximum Power Point Tracking (charge controller technology)
- **PD (Power Delivery):** USB-C fast charging protocol
- **DVFS:** Dynamic Voltage and Frequency Scaling
- **DPM:** Dynamic Power Management
- **Peak Sun Hours:** Equivalent hours at 1000 W/m² solar irradiance
- **Wh (Watt-hour):** Energy consumption unit

---

*Paper Version: 1.0  
Next Review: After Phase 1 completion (estimated 2 weeks)*
