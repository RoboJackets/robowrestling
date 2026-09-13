# 3 kg RoboWrestling Sensor / Motor Interface — KiCad 9, rev 0.4

This revision focuses on schematic readability and correct use of standard KiCad symbols.

## Visual / library cleanup
- Uses stock-style `Device:Battery` for the external LiPo pack.
- Uses stock `Switch:SW_SPDT` symbols for the three mechanically linked poles of the one physical 3PDT Baumer mode switch.
- Uses stock `Motor:Motor_DC` symbols for the two brushed drive motors.
- Uses normal KiCad resistor/capacitor/LED/BJT/fuse/TVS/crystal/test-point/connector symbols throughout.
- Vendor-specific modules/ICs that do not have stock symbols remain custom: Pololu DC/DC modules, Cytron MDD20A, MAX14819A.
- The controller connector is a generic 2x14 connector; function names are now net labels, not baked into a fake library symbol.
- Local signal chains are connected with real wires. Labels are reserved mainly for power rails and long-distance controller/IO connections.

## Controller requirements
- `BAUMER_*_DIG`, `BANNER_*`: 3.3 V digital GPIO inputs; interrupt capability preferred.
- `LINE_*_ADC`: 0–3.3 V ADC-capable inputs.
- `IOLINK_SCK/MOSI/MISO`: hardware SPI.
- `IOLINK_CS_A`, `IOLINK_CS_B`: separate digital outputs.
- `IOLINK_IRQ_A`, `IOLINK_IRQ_B`: interrupt-capable digital inputs.
- `MOTOR_*_PWM`: hardware PWM outputs, <=20 kHz.
- `MOTOR_*_DIR`: ordinary digital outputs.
- `CTRL_UART_TX/RX`: 3.3 V UART for the ESP32 telemetry daughterboard.

## Important
This remains a design-start schematic, not a release-to-fabrication PCB. Verify the MAX14819A vendor reference design/footprint, IO-Link protection network, switch pinout, battery/current sizing, selected regulator modules, and mechanical connector footprints before PCB layout.
