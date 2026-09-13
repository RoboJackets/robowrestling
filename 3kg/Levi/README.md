# Levi — 3 kg robowrestling electronics, revision 1.0

Open **Levi.kicad_pro**, then **Levi.kicad_sch**. The schematic is rebuilt as ten A3 sheets. Local analog, reset, indicator, protection and motor-gating circuits use wires; named nets connect the sheets. Originals are preserved in `design/original/`. The older explanatory PDF, XLSX and `robowrestling_kicad9_design_v2` describe the superseded design.

## Selected architecture

- **Control: ESP32-S3-WROOM-1-N8, without PSRAM.** It accommodates all direct sensor inputs, five ADC channels, two motor channels, SPI and telemetry UART. GPIO35–37 must remain available: do not substitute an octal-PSRAM module. Control firmware should leave its radio off.
- **Telemetry: ESP32-C6-MINI-1-N4.** Independent UART0 programming/reset/boot circuitry; UART1 connects to the S3 through 100-ohm resistors. Telemetry must not delay the control loop.
- **Industrial sensors: regulated 24 V**, using Pololu U3V50F24, replacing S13V25F12. Both Baumer and Banner support 10–30 V. A 12 V supply does not guarantee the MAX14819 receive-high threshold after Baumer output drop. All sensor-rail capacitors are rated 50 V.
- **Logic: Pololu S13V30F5 supplies 5 V; Traco TSR2-2433 supplies 3.3 V / 2 A**, replacing the AP2112K. The logic input has a separate fuse, reverse-blocking diode and TVS. Motor current stays in the external harness.
- **Two MAX14819AATM+** provide three IO-Link channels. Actual 48-pin plus exposed-pad mapping is split into logic, channel and power units. External V5 is used with REGEN grounded. Unused L+ controllers are omitted; SN1/SN2 pairs are connected together, otherwise floating. Firmware must disable unused L+ diagnostics and configure the SPI framer.

## Sheet and harness guide

| Sheet | Function |
|---|---|
| 1 | Power protection, regulators and sheet index |
| 2–3 | Control and telemetry MCUs, programming, reset and boot |
| 4 | Three Baumer O300.DI-GM1J.72N inputs and 3PDT selector header |
| 5 | Three Banner Q20NDXL sensors, both complementary NPN outputs |
| 6–7 | IO-Link masters and crystals |
| 8 | Four ML1 inputs, battery ADC and hardware PWM gating |
| 9 | External battery disconnect, MDD20A and two Pololu 4743 motors |
| 10 | Removable ARM link, default-low resistors and nine debug LEDs |

Baumer/Banner four-pin board headers follow **1 brown supply, 2 white, 3 blue ground, 4 black**. Baumer white is TEACH, held low by 10k. Banner black and white each have a 10k pull-up to 24 V. LM339B comparators produce 3.3 V logic with approximately 5 V raw switching threshold and hysteresis. GPIO HIGH means the corresponding raw line is HIGH; apply the sensor's light/dark polarity in firmware.

ML1 headers are **1 supply (3.3 V), 2 ground, 3 OUT**; connect by the sensor silkscreen. Their 10k/20k dividers limit full-scale ADC input to 2.2 V. The battery divider gives about 2.27 V at a 12.6 V pack. Use ADC attenuation and calibration appropriate to these ranges.

The selector is one mechanically linked, break-before-make 3PDT. Each header group is **digital / common C-Q / IO-Link**. Numbers on its schematic are harness identifiers, not a claim about stamped switch-lug numbers: identify lugs by continuity. Stop motors and disable framers before changing modes.

Programming headers: **GND, 3V3 VREF, MCU TX, MCU RX, EN, BOOT**. Use a 3.3 V UART adapter; VREF is a sense connection, not an additional power input. Hold BOOT, pulse RESET, then release BOOT. Motor header: **GND, PWM_L, DIR_L, PWM_R, DIR_R**, connected to the driver's named terminals. MDD20A PWM LOW means dynamic braking; use PWM at or below 20 kHz.

## Parts, libraries and checks

`BOM.csv` is the revised component list, including purchased sensors and external harness parts. All **207 PCB components** have footprint assignments. External motors, sensors, battery, driver, bulk capacitor/TVS assembly and panel switch intentionally use external placement rather than fictitious PCB footprints. Connector housings, crimp contacts and wire lengths must be purchased to suit the final harness.

Stock KiCad symbols are used where available. Project-local symbols contain the actual vendor pin/terminal maps. The two Pololu footprints follow their mechanical drawings; the MAX14819 footprint uses the **T4877+4C 5.50 mm exposed pad**, with stock KiCad peripheral lands and paste windows. Maintain module clearance, antenna keepouts and access to the regulator mounting holes during layout.

Validation: KiCad 9 ERC has **0 errors and 0 warnings**, all assigned footprints exist and cover the symbol pin numbers, and the exported netlist passes **437 PCB pin-to-net expectations plus 37 independent topology checks**. Reports are in `design/review/`; SVG previews and PNG renders are in `design/review/release/`. These are schematic checks; PCB routing, EMC, thermal behavior and powered hardware have not been tested.

Before full-power operation, verify the 24/5/3.3 V rails with current limiting, program both MCUs with motors disconnected, confirm all sensor polarities, then test the ARM link and physical disconnect. Tune the crystal load capacitors from the actual layout and confirm startup. The 20 A motor fuse is provisional pending measured startup/stall current and harness sizing. The logic ARM gate is not an independent watchdog; firmware must clear MOTOR_ARM on faults and enforce battery cutoff. Select actual capacitors with sufficient effective capacitance under DC bias and matching case dimensions before ordering.

## Vendor references

- [ESP32-S3 module datasheet](https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf), [ESP32-C6 module datasheet](https://documentation.espressif.com/esp32-c6-mini-1_mini-1u_datasheet_en.html)
- [MAX14819 datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/max14819.pdf), [TQFN package drawing](https://mds.analog.com/api/public/content/tqfn_21-0144.pdf)
- [Baumer O300](https://media.baumer.com/Baumer_O300.DI-GM1J.72N_EN_20250909_DS.pdf), [Banner Q20](https://info.bannerengineering.com/cs/groups/public/documents/literature/127816.pdf), [JSumo ML1](https://www.jsumo.com/micro-line-sensor-ml1)
- [U3V50F24](https://www.pololu.com/product/2569), [U3V50 mechanical drawing](https://www.pololu.com/file/0J1450/u3v50x-step-up-voltage-regulator-dimensions.pdf), [TSR2 datasheet](https://www.tracopower.com/sites/default/files/products/datasheets/tsr2_datasheet.pdf)

`design/build_schematic.py` regenerates the schematic and BOM; it is a development helper, not required to edit in KiCad. Regeneration overwrites subsequent manual schematic edits. `design/audit_nets.py` checks an exported KiCad netlist.

## Learning resources

The complete learning handbook is in `output/pdf/Levi_Schematic_Learning_Handbook.pdf`. The searchable offline companion is `output/Levi_Learning_Companion.html`; open it in a browser. Both cover revision 1.0, include worked examples and reference lookups, and explain the battery recommendation and mechanical assumptions.
