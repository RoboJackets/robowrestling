# How to learn Levi

This handbook explains the saved revision 1.0 schematic, not a generic robot circuit. Keep KiCad open beside it. Reference names such as R9 and U30 are search keys: use Find in KiCad to locate them. The reference atlas at the back lists the parts and their actual electrical connections. Full schematic sheets follow the teaching chapters.

Start with three passes. First, spend 20 minutes on the architecture, power tree and battery decision. Second, follow one complete signal from sensor to motor, using the sensor, comparator, ADC and motor chapters. Third, work through the equations, pin atlas and bench exercises. Do not try to memorize 207 PCB components before understanding their repeated patterns.

The schematic is an electrically checked design, not tested hardware. The recorded ERC result is zero errors and warnings; that does not demonstrate immunity to motor noise, adequate thermal margins, successful IO-Link communication or safe fault recovery. This guide marks calculated examples and proposed firmware behavior separately from physical connections already drawn.

## Your learning milestones

| Stage | You should be able to explain | Practical exercise |
|---|---|---|
| System | Where energy flows and who controls motion | Draw the power and information paths from memory |
| Circuit | Why each component family exists | Trace the left Baumer and left PWM channels |
| Quantitative | Voltage scaling, filtering, hysteresis and runtime | Recalculate a divider and a three-minute energy budget |
| Implementation | Pin numbers, startup states and wiring | Find a connector pin and its MCU destination |
| Validation | What ERC cannot establish | Write a test with an instrument, expected result and stop condition |

## How to read the pages

Read a circuit in this order: supply voltage, ground return, input source, transformation, output destination, startup state, and fault behavior. Ask what happens when the input is missing, shorted, noisy or late. Each question teaches more than memorizing a component value.

Values such as 10k mean 10,000 ohms; 100n means 100 nanofarads; 1u means 1 microfarad. A voltage rating on a capacitor is a limit, not the voltage it produces. GPIO numbers identify firmware signals; package pin numbers identify physical pads. They are not interchangeable.

# The whole robot in two flows

The battery supplies an external MDD20A motor driver and a separately fused electronics board. Three regulators create 24 V for industrial sensing, 5 V for the IO-Link transceivers, and 3.3 V for processors and line sensing. All share an electrical ground reference. Motor current must travel through the heavy external wiring, rather than through the control PCB's power header.

Information flows in the other direction: sensors report the environment, conditioning circuits translate voltage levels, the ESP32-S3 makes a decision, and PWM/direction signals tell the driver how to energize the motors. The second ESP32 handles telemetry. It is not electrically isolated: it shares power and ground with the control MCU.

The nine debug LEDs indicate nine digital logic states. They do not independently prove that a sensor has detected an opponent, that its cable is intact, or that firmware interpreted its polarity correctly.

## What each sensor contributes

| Device | Quantity | Electrical information available | Route to control MCU |
|---|---|---|---|
| Baumer O300.DI-GM1J.72N | 3 | Switching output or IO-Link on C/Q | Comparator in DIGITAL mode; MAX14819 in IO-Link mode |
| Banner Q20NDXL | 3 | Two complementary NPN outputs per sensor | Six comparator channels |
| JSumo ML1 | 4 | Analog line/reflectance output | Four divided and filtered ADC1 inputs |
| Battery divider | 1 | Total pack voltage | Fifth ADC1 input |

The optical sensors require installation and calibration. Their names in the schematic identify electrical channels; the drawing does not define sensor aim, wheel geometry, reflective thresholds or a winning control algorithm. Those depend on the mechanical robot and arena.

## A complete example

Suppose the left Baumer's C/Q line becomes HIGH while the selector is in DIGITAL. The signal enters J4 pin 4, reaches the common contact of the left switch pole through J7, and returns as BAUM_L_DIGRAW. R9/R10/C14/R12 condition it; U20A compares it with SENSE_REF. R11 supplies the comparator's HIGH level. BAUM_L reaches S3 GPIO7 and the buffered indicator channel Q1/D6. Firmware may then change PWM_L_RAW and DIR_L_RAW. U40 gates PWM with MOTOR_ENABLE, R69 feeds PWM_L, and J15 connects it to MDD20A PWM1. The driver switches battery current through M1.

Notice the boundaries: the sensor does not directly power the motor, and the MCU does not directly drive motor current. The software decision is a required step between sensing and motion.

# Read the schematic like a circuit designer

## Symbols, wires and labels

A wire is a conductive connection. A junction dot explicitly joins branches. A crossing without a junction is not an intended connection; use KiCad Highlight Net when uncertain. Labels with the same global name connect electrically even on different sheets. A sheet box on the root page is navigation, not an electronic component.

GND is the common reference node. It is not automatically chassis earth and does not imply that return-current paths have zero impedance. A motor return wire carrying several amps can develop enough voltage to disturb a logic reference. Board layout and harness routing determine that behavior.

An X at a pin is an intentional no-connect marker. Leaving a pin unused is different from tying it LOW. PWR_FLAG is an ERC annotation saying that an external source drives a net; it does not add a regulator, fuse or physical footprint.

## Multi-unit components

U20A through U20E are one physical LM339 package: four comparators and a power unit. U30's four units are one MAX14819 package, divided to make the logic, channels and power pins readable. SW101A/B/C are the three mechanically linked poles of one switch. U40's power unit is on sheet 10 while its gates are on sheet 8. Always search all units before deciding that power pins are missing.

## Footprints and reference numbering

The symbol describes electrical meaning; the footprint describes copper pads and mounting geometry. A correct pad count alone does not prove that a land pattern has adequate soldering or thermal performance. The local Pololu footprints include the module outline and mounting holes, not just a row of connector pads.

R, C, D, Q, U, J, F, SW, Y and TP identify resistors, capacitors, diodes, transistors, integrated circuits/modules, connectors, fuses, switches, crystals and test points. A1 is the external motor-driver module; BT1 is the battery. Purchased sensors have BOM identifiers but are represented electrically by their board-side harness connectors.

# Power: battery to three regulated rails

Start on sheet 9: BT1 positive passes through F100 and the removable power link SW100 to BAT_FUSED. The driver receives this bus directly. J1 brings a small branch to sheet 1. F1 then feeds D1, which feeds LOGIC_IN. D2 and C1 connect from that protected rail to ground.

| Part | Actual role | What it does not do |
|---|---|---|
| F100, provisional 20 A inline fuse | Limits consequences of a sufficiently large harness fault | Does not detect a motor stalled at 5.5 A |
| SW100, removable XT60 link | Physically interrupts the positive battery path | Does not discharge every capacitor instantly |
| F1, 0451002.MRL 2 A | Separate electronics-branch protection | Does not guarantee every regulator's current stays below 2 A |
| D1, SS34 | Blocks reverse input into electronics | Does not protect the external MDD20A against reverse polarity |
| D2, SMBJ13A | Shunts positive input transients | Is not a precision 13 V regulator |
| C1, 47 uF / 35 V | Local input energy reservoir | Does not replace a battery or absorb unlimited braking energy |
| F2, 1812L050/30 | Resettable 0.5 A-hold sensor-rail protection | Does not provide instant per-port current limiting |

Fuses respond to current and time. A 2 A marking is not a perfect 2.000 A ceiling. A resettable fuse increases resistance as it heats; ambient temperature changes its behavior. Select and test fuse coordination using actual inrush, fault current and wiring.

## Why three regulators?

U1, Pololu U3V50F24, boosts the battery-derived input to +24V_RAW. F2 feeds +24V_SENS. U2, Pololu S13V30F5, supplies +5V. U3, Traco TSR2-2433, supplies +3V3. The EN pins of the Pololu modules are left open to use their documented internal enable behavior. These are complete switching-regulator modules; their inductors and switching ICs are inside the modules, not missing PCB parts.

C2 and C5 are 22 uF / 50 V reservoirs for the 24 V rails; C3 is 22 uF / 25 V on 5 V; C4 is 22 uF / 10 V on 3.3 V. Voltage rating alone does not specify capacitance under bias, ESR, temperature performance or ripple-current capability. The current BOM specifies values and packages for many passives, rather than a purchasing-qualified MPN for every capacitor.

## Power is conserved, current is not

For a regulator, input current is approximately output power divided by input voltage and efficiency. If the 24 V rail supplies 0.20 A, it delivers 4.8 W. At 10.5 V input and an assumed 85% efficiency, input current is about 0.54 A, before other loads. This is an example, not a measured Levi current budget.

An LDO making 3.3 V from 12 V at 0.5 A would dissipate about 4.35 W. That explains the choice of a switching 3.3 V supply. A 2 A regulator rating is available capacity, not a claim that the circuit always draws 2 A.

# Main controller: why the S3 and how it starts

U10 is ESP32-S3-WROOM-1-N8 without PSRAM. The application consumes 28 GPIO signals: five analog inputs, nine digital sensor inputs, seven IO-Link interface signals, five motor signals and two telemetry signals. UART0 programming and BOOT are additional. The choice fits this direct-I/O architecture; it is not a claim that S3 is universally superior to every MCU.

GPIO1, 2, 4, 5 and 6 are used as ADC1 inputs. GPIO35-37 are used for IO-Link; substituting a module that reserves them for octal PSRAM would break the design. GPIO3/45/46 are intentionally unused strapping pins. GPIO0 is BOOT. USB pins 19/20 are unused in this revision.

## Reset and boot are different operations

R1 pulls CTRL_EN toward 3.3 V and C9 slows its rise. Their nominal time constant is 10k x 1uF = 10 ms; the actual release time depends on input thresholds and supply ramp. SW1 pulls EN LOW to reset. R2 normally holds GPIO0 HIGH; SW2 pulls BOOT LOW. Holding BOOT while resetting selects the serial download path. This is not an automatic USB programming circuit.

C6, C7 and C8 are 100 nF, 10 uF and 47 uF in parallel across the local supply. The small capacitor helps at higher frequencies when placed close to the module; larger values support slower load changes. Physical trace inductance prevents a distant capacitor from behaving like an ideal capacitor at the pin.

J2 is the control programming header. Its 3.3 V pin is VREF for a compatible adapter, not permission to connect an independent 3.3 V power source. MCU TX connects to adapter RX and vice versa. Use common ground and 3.3 V logic.

## Firmware obligations

At startup, keep MOTOR_ARM and both PWM commands LOW. Configure ADC attenuation/calibration, sensor GPIOs, SPI chip selects and timeouts before arming. Hardware PWM generates regular pulses; it does not decide whether movement is appropriate. A proposed control loop should give edge detection priority, reject stale sensor data, handle battery limits and refresh a watchdog. Those behaviors are requirements to implement, not firmware already supplied with this schematic.

Dual-core capability is useful scheduling headroom, but assigning a task to a core does not by itself make it real-time. Interrupt load, locks, flash operations and blocking logging can still introduce latency.

# Telemetry and service connections

U11 is ESP32-C6-MINI-1-N4. GPIO18 receives TELEM_RX from S3 GPIO42 through R3. GPIO19 transmits TELEM_TX through R4 to S3 GPIO47. Both series resistors are 100 ohms. They reduce edge-related ringing and limit small contention currents; they are not level shifters or isolation barriers.

R5/C13/SW3 provide reset, R6/SW4 provide BOOT, and R7 holds GPIO8 HIGH for the intended download strapping condition. J3 is a separate UART0 service header. C10-C12 provide local bypassing. A radio-current transient on this module can still affect the shared 3.3 V rail if the supply and layout are poor.

## Suggested packet contract

Use a framed message containing a version, sequence number, timestamp, payload length, payload and CRC. Report raw sensor values, interpreted states, battery voltage, commanded PWM, mode and faults. Include a receiver timeout. This is a suggested interface, not an existing software protocol. Losing telemetry must not prevent local edge avoidance.

| Connection | Control end | Telemetry end | Meaning |
|---|---|---|---|
| Outbound telemetry | GPIO42 / CTRL_TX | GPIO18 / TELEM_RX | S3 transmits robot state |
| Return serial data | GPIO47 / CTRL_RX | GPIO19 / TELEM_TX | C6 transmits to S3 |
| Programming | J2 UART0 | J3 UART0 | Independent firmware loading |
| Reference | +3V3 and GND | +3V3 and GND | Shared supply, no galvanic isolation |

Do not let a debug command bypass the motor-arming rules. A communications processor is a separate scheduling domain, not automatically a safety boundary.

# Baumer switching inputs and mode selection

Each Baumer cable uses brown for positive supply, blue for ground, black for C/Q, and white for TEACH. J4, J5 and J6 are board-side four-pin connectors. Their numbered arrangement follows the documented M8 electrical assignments; the PCB connector itself is JST-XH, not an M8 connector.

R8/R13/R18 hold TEACH LOW. TP1/TP2/TP3 expose those lines. They are industrial-voltage signals, not 3.3 V GPIO test points. Do not inject arbitrary teach pulses without following the sensor's teach procedure.

D3-D5 are SMCJ48A TVS devices on the three C/Q lines. Their job is transient suppression. Their value does not mean that normal C/Q is 48 V. ADI discusses this device family for specified surge environments; the complete installed harness still needs a protection and signal-integrity check.

## Follow the selector carefully

J7 has three groups: pins 1/2/3 for left, 4/5/6 for center, and 7/8/9 for right. Each group is digital path / sensor C/Q common / IO-Link path. SW101 is one 3PDT switch. The numbers in its custom harness symbol are logical wiring identifiers; identify the physical switch lugs by continuity before assembling the harness.

In DIGITAL, C/Q reaches the comparator input. In IO-Link, it reaches the corresponding MAX14819 C/Q pin. The disconnected digital divider tends toward LOW; it is not a valid sensor reading in that mode. There is no dedicated switch-position input in this schematic, so firmware needs an explicit configuration or a carefully designed mode-detection procedure. Do not assume the MCU can directly read SW101's position.

## What the digital conditioner does

The left channel uses R9 = 30k from the raw line, R10 = 10k to ground, C14 = 1 nF to ground, R12 = 1M positive feedback, U20A, and R11 = 4.7k output pull-up. Center and right repeat the circuit with different reference numbers. The next chapter derives it once so you can understand all nine instances.

# Comparator circuit: derive every important number

The LM339B compares its positive and negative inputs. Its output is open collector: it can pull LOW, but it cannot actively drive HIGH. R11 supplies the HIGH level from 3.3 V. Powering the comparator from 24 V does not make its pulled-up output 24 V. This is the voltage-domain translation in the design.

R23 and R24 generate the shared reference; C18 filters it. Nominally Vref = 3.3 x 10 / (16.5 + 10) = 1.2453 V. This is a resistor-derived reference, not a precision reference IC. Its voltage follows the 3.3 V rail and resistor tolerances.

Ignoring feedback first, 30k/10k scales a raw input by 1/4. A 24 V input becomes approximately 6 V at the comparator input, which is why the comparator itself is powered from the industrial rail. This node must never be routed directly into the ESP32.

## Positive feedback creates hysteresis

At the transition, the positive input equals Vref. Kirchhoff's current law gives:

Vraw,trip = Vref x (1 + 30k/10k + 30k/1M) - Vout x (30k/1M).

With the output LOW at an illustrative 0.2 V, the rising threshold is about 5.012 V. With the output HIGH at an ideal 3.3 V, the falling threshold is about 4.920 V. The separation is about 93 mV referred to the raw input. The actual HIGH is slightly loaded by feedback and the indicator transistor circuit, and actual offsets/tolerances shift these values. These are nominal calculations, not guaranteed limits.

Without hysteresis, a slowly moving or noisy input near threshold could make the output chatter. Positive feedback makes the switching threshold depend on the previous state. The capacitor adds a different effect: it attenuates fast changes continuously.

## Filter and loading

With an ideal low-impedance raw source, the resistance seen by C14 is roughly 30k || 10k || 1M = 7.44k. Its time constant is approximately 7.44 us and its single-pole corner is about 21.4 kHz. The source impedance changes that calculation; this matters particularly for the Banner pull-up circuit.

At 24 V, the simple 40k divider path draws around 0.6 mA. The 30k resistor dissipates about 10.8 mW in the no-feedback approximation. R11 supplies roughly (3.3 - 0.2)/4.7k = 0.66 mA when the output is LOW. These values explain why ordinary small resistors are appropriate here.

## Unused comparators and failure signatures

Unused units have their positive input grounded, negative input tied to SENSE_REF, and output marked unconnected. Their power pins still belong to the same physical IC. A missing 3.3 V rail can corrupt both Vref and output levels. A missing 24 V rail can invalidate comparator behavior even if the MCU remains powered. Firmware should not equate a stable digital value with proof that all rails are healthy.

# Banner NPN inputs: why the pull-ups matter

J8-J10 bring in the three Q20NDXL sensors. Each has a black and white complementary NPN output. An NPN output sinks current when ON; when OFF it needs an external pull-up to establish a HIGH voltage. The six 10k pull-ups connect to +24V_SENS. Six comparator channels then translate the raw lines to 3.3 V logic.

The raw HIGH is not exactly 24 V. A 10k pull-up feeding an approximately 40k divider produces about 19.2 V before feedback and leakage are considered. With an illustrative 200 uA worst-case leakage allowance, that becomes roughly 17.6 V. Both remain well above the approximately 5 V decision threshold. Check the exact output specifications for the purchased suffix. When ON, the sensor pulls the line close to ground and the comparator output becomes LOW.

The 10k pull-up dissipates at most about 24.96 squared / 10,000 = 62 mW if its output is pulled to ground at the upper 24 V regulator tolerance. That is below a nominal 125 mW resistor rating at its specified temperature, although board temperature still requires derating.

## Complementary does not mean self-validating

The two outputs should usually represent opposite optical states once switching has settled. Sampling during transitions, disconnecting the sensor, or losing sensor power can produce combinations that are not meaningful detection states. Debounce or validate the pair over time; use a fault state rather than forcing every combination into opponent/no-opponent.

Use the sensor's light/dark operating definition to map electrical HIGH/LOW to detection. An LED marked BAN_L_BK lights for logic HIGH, not automatically for 'opponent left'. Distinguish electrical polarity from semantic meaning in both code and telemetry.

# IO-Link: physical layer, framer and software

U30 connects left and center; U31 connects right and has one unused channel. SPI is shared; chip selects and interrupts are separate. The S3 never sees 24 V C/Q directly. The MAX14819 translates between the industrial line and its low-voltage digital interface.

The IC includes framing assistance, but it is not a complete application that automatically returns distance readings when power is applied. The host must configure communication, handle startup and timeouts, process messages, and interpret sensor-specific process data using the correct device documentation/IODD. IO-Link is not interchangeable with a plain 3.3 V UART cable.

## Read the four units of one IC

The logic unit contains CS, SCLK, SDI, SDO, IRQ, address and clock pins. Channel units contain C/Q, direct TX/RX controls and optional supply-controller signals. The power unit contains VCC, VL, V5, REGEN, exposed ground and NC pins. The reference atlas lists the exact package pin mapping.

The schematic ties TX/TXEN LOW for the intended internal-framer use, uses separate CS lines with A0/A1 LOW, and leaves unused status outputs disconnected. L+ controllers are omitted: sensors receive shared fused power directly. SN1/SN2 pairs are tied together and otherwise floating. Firmware must disable the unused L+ fault reporting; there is no individual software-switched sensor power channel in this revision.

## Supplies and clocks

VCC is 24 V, VL is 3.3 V, and external V5 is 5 V with REGEN grounded. This avoids dissipating the full 24-to-5 V drop in the chip's internal regulator. Local capacitors are distinct from the large supply reservoirs and must be placed by the relevant pins.

Y1/Y2 are specified as 14.7456 MHz crystals with 18 pF load capacitance. C27/C28 and C33/C34 are initial 22 pF external values. For a symmetric oscillator, effective load is approximately half the per-leg capacitance, including internal and parasitic contributions. The design's initial estimate is (22 + 10 + 4)/2 = 18 pF. This is a layout-dependent estimate, not a measured oscillator result. Confirm the ordered crystal package, ESR, startup and frequency.

## Why 24 V replaced 12 V

Both industrial sensor models accept the higher rail. With a 12 V supply, the Baumer output drop can leave too little guaranteed HIGH-level margin for the MAX receiver. Raising the rail creates margin; it does not remove the need to check polarity, wiring and surge conditions. The MAX footprint's exposed pad is 5.50 mm for the selected package and must connect to a suitable ground/thermal structure.

Start SPI at the documented design target of 1 MHz, verify register communication, then bring up one IO-Link channel before all three. Exact register values and sensor process-data decoding belong in a separately tested driver; this guide deliberately does not invent unverified register writes.

# Analog edge sensing and battery measurement

The four ML1 sensors are supplied from 3.3 V through J11-J14. Their output passes through 10k, then reaches a node with 20k and 10 nF to ground. That node feeds ADC1. Local 100 nF capacitors bypass each sensor supply connection.

Vadc = Vsensor x 20/(10+20) = 2/3 x Vsensor. Therefore a 3.3 V output becomes 2.2 V. The source resistance seen by the capacitor is nominally 10k || 20k = 6.67k, giving tau = 66.7 us and fc = 2.39 kHz. Approximately five time constants, 0.33 ms, brings a step close to its final value when the source behaves ideally.

Do not assume that a 12-bit ADC code directly equals code/4095 x 3.3 V. Attenuation, calibration, nonlinearity and sampling behavior matter. Convert to calibrated millivolts first. Then Vsensor is approximately 1.5 x Vadc. Calibrate thresholds over actual dark/light surfaces at the installed height and ambient lighting.

## Battery divider

R67 = 100k, R68 = 22k and C47 = 100 nF. Vadc = Vpack x 22/122. The reverse conversion is Vpack = Vadc x 122/22, or about 5.545 x Vadc. At 12.6 V, Vadc is 2.272 V. At 10.5 V, it is 1.893 V.

The divider continuously draws about 103 uA at 12.6 V while BAT_FUSED is energized. Its nominal filter resistance is 18.03k, time constant 1.80 ms, and corner 88.3 Hz. This helps reject short noise spikes but also delays a sudden voltage change.

| Measured ADC voltage | Inferred pack voltage | Interpretation |
|---|---|---|
| 2.272 V | 12.60 V | Nominal full charge of a standard 3S LiPo |
| 2.002 V | 11.10 V | Nominal pack voltage, not a precise state of charge |
| 1.893 V | 10.50 V | 3.5 V/cell average; candidate stop threshold |

This circuit measures the sum of all three cells. It cannot identify a weak cell or perform balancing. A pack could have an acceptable total while one cell is too low. Check individual cells with an appropriate balance charger/checker between runs. Select stop thresholds using cell guidance and measured load sag, rather than running down to an absolute minimum.

# Motors, PWM and the enable chain

U40 is a dual AND gate. One input receives PWM_L_RAW or PWM_R_RAW; the other receives MOTOR_ENABLE. Each output reaches the driver through a 100-ohm resistor and has a 10k pull-down. DIR_L_RAW and DIR_R_RAW reach the driver through separate 100-ohm resistors.

J16 is a removable link between MOTOR_ARM and MOTOR_ENABLE. R75 and R76 pull those signals LOW. R77-R80 pull the raw PWM and direction commands LOW during reset or high-impedance states. These are passive startup defaults, not firmware supervision.

| MOTOR_ENABLE | PWM_RAW | Gated PWM | Result at driver |
|---|---|---|---|
| LOW | LOW or HIGH | LOW | Dynamic brake mode |
| HIGH | LOW | LOW | Dynamic brake portion of PWM |
| HIGH | HIGH | HIGH | Drive in the direction selected by DIR |

MDD20A PWM LOW means brake, not coast. Therefore removing ARM does not electrically disconnect the motor driver. SW100 is the physical battery disconnect. The driver also has local test buttons; these belong to the external module and must be considered when working near the robot.

## PWM is not a speed sensor

Duty cycle controls the driver command. Motor speed still depends on voltage, load, friction and traction. The selected Pololu 4743 has no encoder, and the schematic contains no motor-current sensor. You cannot claim closed-loop wheel speed or measured stall detection from this hardware alone.

At 12 V the motor's published no-load speed is 200 RPM and extrapolated stall current is 5.5 A. A full 3S pack is 12.6 V, slightly above the nominal motor rating. A simple first-order voltage compensation would limit full-pack duty to 12/12.6 = 95.2%, but PWM still applies full bus-voltage pulses; this is not a guarantee of identical motor stress.

Rapid reversal while a motor is spinning can cause a current transient above stationary stall current because back EMF initially opposes the new command. Ramp or manage direction changes, and validate current with instrumentation. The 20 A/channel driver rating is capacity, not what each motor always draws, and its own current limit is not tailored to a 5.5 A-stall motor.

## The missing protection boundary

There is no independent external watchdog or per-motor current sensing in revision 1.0. A frozen MCU that leaves MOTOR_ARM HIGH can leave the gate enabled. MCU watchdog reset helps only if correctly configured and able to reset the relevant outputs. For a competition-ready implementation, evaluate independent timeout/current protection against the event's requirements and measured fault behavior. Do not use a prolonged stall as a battery-runtime test.

# Debug LEDs, layout and component details

Each digital indicator uses a 47k base resistor, MMBT3904 transistor, green LED and 1k series resistor. The MCU/sensor logic drives the transistor base; the LED current comes from 3.3 V. This prevents the LED itself from becoming a large load on the comparator output.

With an illustrative 0.7 V base-emitter drop, base current is about (3.3 - 0.7)/47k = 55 uA. With an illustrative green LED drop of 2.0 V and transistor drop of 0.2 V, LED current is roughly 1.1 mA. Actual LED color chemistry and transistor gain affect brightness and saturation. LED lit means the electrical net is HIGH.

The transistor symbol pins matter: the atlas gives the actual numbered connections. Do not assume every SOT-23 transistor has the same pin order. Likewise, a diode's cathode marking and an electrolytic capacitor's polarity must match the assembled footprint and rail.

## Physical placement changes circuit behavior

Put bypass capacitors near the pins they serve with short ground returns. Route crystal traces short and quiet. Keep antenna areas clear according to the exact module documentation, including nearby metal. Keep sensor return wiring and logic references away from the main motor-current loop. Twisting motor pairs and routing signal/return pairs together can reduce loop area; the final EMI performance must still be measured.

The +24 V boost module is about 48.3 x 15.2 mm in its manufacturer drawing and is taller than a bare PCB. Its footprint outline is not the entire clearance envelope once headers and standoffs are installed. Maintain clearance for mounting hardware and access to connectors.

The SMCJ/SMBJ designations specify package families and electrical families, but final ordering requires a vendor and exact suffix. The BOM's LM339BIDR should be checked against the TI LM339B datasheet; some inherited stock-symbol datasheet fields point to an older generic LM339 document. The guide's source list identifies the intended vendor documentation.

## Transient protection is conditional

A TVS has a working standoff voltage, a breakdown region and a higher clamping voltage at a stated pulse current. SMBJ13A's nominal maximum clamp specification is close to the 5 V Pololu module's 22 V input limit. Wiring inductance and actual surge amplitude still need verification. Do not interpret a passing ERC as proof of adequate transient margin. The 24 V supply is also not a certified industrial IO-Link port merely because the nominal voltage is correct.

# Battery selection: a concrete starting pack

Recommended baseline: Tattu 1300 mAh 3S 75C with XT60, manufacturer part TA-75C-1300-3S1P-XT60, store SKU TAA13003S75X6. It is a standard 3S LiPo: 11.1 V nominal and 12.6 V fully charged. Published body dimensions are 72 x 36 x 22 mm; mass is 122 g with a stated +/-20 g tolerance. It has XT60 discharge and JST-XHR balance connections. Source B1 is the manufacturer purchase/specification page.

This recommendation assumes approximately a three-minute match, swaps between runs, and space for the pack and protected wiring. Final fit is not established without the battery compartment and remaining robot weight budget. It is not necessary to choose an enormous pack just because the driver says 20 A per channel.

## Derive the electrical requirement

At 12.6 V, scaling the published 12 V stationary stall current gives 5.5 x 12.6/12 = 5.78 A per motor, or 11.55 A for two. Allocate an illustrative 2 A battery-side allowance for electronics and conversion losses to obtain a 13.55 A sizing case. This allowance is a conservative scenario, not a measured load or a statement that F1 carries exactly 2 A continuously.

For a three-minute run, required usable charge at 13.55 A is 13.55 x 3/60 = 0.678 Ah. If only 80% of nominal capacity is budgeted, required nominal capacity is about 0.847 Ah. A 1.3 Ah pack provides useful reserve. The motors cannot safely sustain that stall operating point for three minutes; it is a conservative capacity calculation only.

A practical provisional battery target is at least 20 A continuous capability with transient headroom, subject to measurement of reversals, wiring and pack sag. The advertised 75C multiplied by 1.3 Ah is 97.5 A. Treat that as a manufacturer rating, not an independently verified current capability and not the robot's expected draw.

## Runtime sensitivity, not a runtime promise

Using 80% of a 1.3 Ah pack, estimated runtime is 60 x 1.3 x 0.8 / average battery amps.

| Average battery current | Calculated duration | How to use it |
|---|---|---|
| 3 A | 20.8 minutes | Light-load scenario only |
| 6 A | 10.4 minutes | Illustrative mixed driving |
| 10 A | 6.24 minutes | Heavy average electrical load |
| 13.55 A | 4.61 minutes | Capacity envelope, not permissible continuous stall |

Capacity varies with temperature, age, current and voltage cutoff. Real runtime must be measured in a representative drive cycle. Keep setup time and retries inside the energy budget.

# Battery alternatives and mechanical integration

All three candidates below are standard 3S, 11.1 V nominal, 75C-labelled packs with XT60. These are alternatives for different space/weight/runtime priorities, not interchangeable mechanical parts.

| Candidate | Exact identifier | Published body / mass | Reason to choose |
|---|---|---|---|
| Baseline 1300 mAh | TA-75C-1300-3S1P-XT60 / TAA13003S75X6 | 72 x 36 x 22 mm; 122 g +/-20 g | Compact starting choice with reserve |
| Lighter 1050 mAh | TA-75C-1050-3S1P-XT60 / TAA10503S75X6 | 71 x 36 x 19 mm; 98 g nominal | Save about 24 g; less reserve |
| Longer 1800 mAh | TA-75C-1800-3S1P-XT60 / TAA18003S75X6 | Description: 105 x 35 x 19.3 mm; 159 g +/-20 g | More capacity in a longer, flatter shape |

The 1800 mAh page is internally inconsistent: its Specs table says 106 x 36 x 19 mm, with length +/-5 mm and width/height +/-2 mm. Use a conservative body envelope of 111 x 38 x 21.3 mm pending supplier confirmation. Do not silently use the smaller numbers to design a tight pocket.

For the baseline pack, the stated dimensional tolerances give a maximum listed body envelope of 77 x 38 x 24 mm. An initial CAD cavity of about 81 x 42 x 28 mm leaves 2 mm per side beyond that envelope for padding/assembly; that cavity is an engineering starting allowance, not a manufacturer dimension. It does not include the lead exit, XT60, balance plug or bend radius. Add a separate cable/connector bay based on the actual pack. The published discharge lead length is 100 mm with 12 AWG wire; the balance lead is listed as 45 mm.

Use a supported tray, a restraint that prevents movement, smooth insulated surfaces and clearance from screws, gears and sharp edges. Do not clamp a soft LiPo pack rigidly between metal plates or rely on crushing foam to accommodate a pack that no longer fits. Remove damaged or swollen packs from service using manufacturer guidance. Put the mass low and close to the intended center of gravity while protecting it from impact.

The cited manufacturer pages provide dimensions, weight, connector and wire data. They do not establish a certified STEP model or production tolerance drawing. Measure the delivered pack before finalizing its mount. At a stated upper baseline mass of 142 g, plus restraint and wiring, allocate more than the nominal 122 g in the 3 kg mass budget.

## Charging and cutoff

Use standard LiPo 3S balance mode, 4.2 V per cell maximum, not LiHV mode. A conservative 1C charge rate for the baseline is 1.3 A if permitted by the delivered pack instructions. Connect the main and balance leads as required by the charger. Charge attended in an appropriate location and store at the manufacturer's storage setting rather than full charge.

The manufacturer manual recommends 3.5 V/cell cutoff for Tattu UAV packs. That corresponds to 10.5 V only when the cells are balanced. Use it as a conservative starting design target, then validate sag filtering and individual-cell behavior; do not treat a total-pack ADC as a balancing or cell-protection system. The MDD20A undervoltage threshold is not a suitable 3S LiPo state-of-charge policy by itself.

# Bring-up: learn by measuring

Work from low energy to high energy. This sequence is a proposed validation plan, not a record of tests already performed. Record instrument readings, firmware version and schematic revision so results remain traceable.

| Step | Instrument / setup | Expected evidence | Stop and investigate if |
|---|---|---|---|
| Unpowered checks | DMM continuity and inspection | Correct polarities, no hard rail shorts, correct selector mapping | Reversed diode/capacitor, unknown switch lugs or connector mismatch |
| Electronics rails | Current-limited supply, motors disconnected | About 24 V, 5 V and 3.3 V; sensible idle current | Heating, collapsing rail or current-limit cycling |
| MCU service | 3.3 V UART adapter | Both MCUs can independently reset and load firmware | Boot depends on unplugging unrelated sensors |
| Analog injection | Known low-voltage source and DMM | ML1 ADC node about 2/3 of injected voltage | Any ADC pin approaches its input limit |
| Comparator channel | Controlled raw input, scope/DMM | LOW/HIGH transitions around the calculated threshold | Chatter, rail-dependent errors or unexpected polarity |
| Sensor installation | Actual arena surface and target | Repeatable raw and interpreted states | Thresholds overlap across intended surfaces |
| IO-Link | Scope/logic analyzer, one sensor first | Reliable SPI, startup, data and timeout recovery | A channel fault blocks all sensing |
| Motor logic | Scope on J15, driver initially disconnected | No PWM when ARM link absent; correct duty/direction | Startup pulse or persistent enable after reset |
| Drivetrain | Secured chassis, low duty, current measurement | Correct wheel direction and controlled stopping | Excess current, mechanical binding or unintended movement |
| Noise and fault tests | Scope plus recorded telemetry | Stable rails, graceful stale-data and reset handling | Radio/motor bursts reset the control MCU |

When probing a switching motor output, do not attach an earth-referenced oscilloscope ground clip to an arbitrary motor terminal. Use a suitable differential/isolated measurement arrangement and understand the instrument's grounding. Probe logic relative to the intended ground reference.

The first measurements should establish actual idle electronics current, peak radio current, motor startup current, battery sag and PWM timing. These turn the battery estimate and fuse choice into evidence-based choices.

# Troubleshooting by symptom

| Symptom | First measurements | Likely paths to investigate |
|---|---|---|
| MCU resets when motors start | 3.3 V and LOGIC_IN at the MCU/regulator | Ground bounce, wiring resistance, regulator transient response |
| Baumer always LOW | Selector position, 24 V, raw C/Q, Vref | IO-Link mode selected, cable pinout, teach configuration |
| Banner polarity seems backwards | Both raw outputs and both GPIO states | Light/dark interpretation versus NPN electrical polarity |
| Line sensors misclassify edges | Calibrated ADC voltage on real surfaces | Height, ambient light, output range, filter/sampling settings |
| SPI works but IO-Link does not | Clock, C/Q, framer setup and device identity | Host stack, mode switch, timing, sensor process-data configuration |
| Motors brake when disabled | PWM LOW on J15 | Expected MDD20A behavior; not coast |
| LED and software disagree | Probe the named GPIO net | Sampling/semantic inversion or wrong channel mapping |
| Pack voltage looks fine but runtime is poor | Per-cell voltage and loaded sag | Weak cell, ageing, excess mechanical load, wrong current assumption |

Use binary isolation: establish the signal at the connector, then after conditioning, then at the MCU, then in software. Replacing components before locating the boundary often hides the original problem.

# Exercises and worked answers

Try these without reading the answers. Use the schematic and a calculator, then explain the result aloud.

1. An ML1 produces 2.7 V. What should its ADC node be? What sensor voltage corresponds to a calibrated ADC reading of 1.4 V?
2. BAT_ADC measures 2.0 V. What pack voltage does that imply? Can it prove all cells are healthy?
3. Why does a 24 V-powered comparator deliver a 3.3 V HIGH? What happens if its output pull-up is missing?
4. If the 1M positive-feedback resistor were removed, what changes and what stays the same?
5. Both motors draw 5.5 A. Why might a 20 A main fuse remain intact while the motors overheat?
6. MOTOR_ARM is HIGH but the removable ARM link is absent. What reaches the driver PWM input?
7. How much nominal capacity supports a three-minute, 10 A average run with 20% reserve?
8. In IO-Link mode, can firmware use BAUM_L as a valid digital opponent input? Can it directly read the switch position?
9. How can two processors still fail together despite separate firmware?
10. Why is 75C x 1.3 Ah not a prediction that Levi draws 97.5 A?

## Answers

1. 1.8 V at the ADC; 2.1 V inferred sensor output. The divider ratio is 2/3.
2. About 11.09 V. No: it measures total voltage, not individual cells.
3. The open collector pulls down while the resistor pulls up to 3.3 V. Without the pull-up, HIGH is not reliably established.
4. Hysteresis disappears. The divider and capacitor still scale/filter the input; the nominal switching reference remains.
5. The combined 11 A is below 20 A. Fuse time-current behavior and motor thermal limits are different protections.
6. R76 holds MOTOR_ENABLE LOW; the AND output is LOW, commanding the driver's brake state.
7. 10 x 3/60 / 0.8 = 0.625 Ah, before extra operational reserve and ageing allowance.
8. No to both in the current hardware. The digital path is disconnected and no mode-sense GPIO exists.
9. They share the supply, ground, environment and serial connection; electrical faults can cross those boundaries.
10. C-rating is a claimed delivery capability. The load determines current, subject to voltage, resistance and dynamics.

## Final teach-back challenge

Explain one left-side sensing-to-motion path, then explain why the robot remains stopped during programming. Point to every component responsible. Finally, identify which part of your explanation depends on firmware and which part depends on physical wiring. If you can do that, you understand the architecture rather than only its labels.

# Sources and how to use the reference atlas

The following links identify primary documentation and battery specifications checked on 2026-09-10. Product pages can change; match the exact suffix and delivered label. The project files are the source for the actual connections and component values in this handbook.

| ID | Source / purpose |
|---|---|
| S1 | ESP32-S3-WROOM-1 module datasheet: pin allocation, boot and module constraints |
| S2 | ESP32-C6-MINI-1 module datasheet: pin allocation, boot and service interface |
| S3 | Analog Devices MAX14819/MAX14819A datasheet: physical layer, clock, supply and framer requirements |
| S4 | TI LM339B datasheet: comparator behavior and electrical limits |
| S5 | Baumer O300 sensor datasheet: cable assignments and operating requirements |
| S6 | Banner Q20 manual: NPN outputs and wiring |
| S7 | JSumo ML1 product documentation: sensor supply and interface |
| S8 | Cytron MDD20A manual: terminal assignments and brake/drive behavior |
| S9 | Pololu 4743 product page: motor electrical/mechanical characteristics |
| S10 | Pololu U3V50F24 and mechanical drawing: boost module and body geometry |
| S11 | Traco TSR2 datasheet: 3.3 V regulator |
| B1 | Tattu 1300 mAh exact product page: recommended pack, dimensions and tolerances |
| B2 | Tattu 1050 mAh manufacturer page: lighter alternative |
| B3 | Tattu 1800 mAh exact product page: longer alternative and conflicting dimensions |
| B4 | Gens ace/Tattu battery manual: charging and cutoff guidance |

The next sections are generated from the saved files. A net named Net-(...) is a local wire without a human-assigned label, not an unresolved connection. NC means explicitly marked unconnected. External harness parts are intentionally excluded from the PCB netlist; their wiring is shown on sheet 9. The complete symbol-pin atlas includes unused and power pins so you can distinguish intentional omissions from missing information.
