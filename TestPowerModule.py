#!/usr/bin/python3#

# Internal libraries under test
from Power.Consumption import Consumption
from Power.BatteryPack import BatteryPack
from Power.BatteryCell import BatteryCell

if __name__ == "__main__":
    batteryCell = BatteryCell(2.10, 5.0, 10, BatteryCell.AGM)
    liFePoBatteryCell = BatteryCell(3.65, 2.5, 5, BatteryCell.LI_FE_P_O4)
    assert liFePoBatteryCell > batteryCell

    try:
        batteryCell.consume_energy(10)
        assert False, "Expected ValueError: Battery cell current draw not set in BatteryCell.update_ampere() before Simulator.run() called."
    except ValueError:
        pass  # test passes

    batteryCell.update_ampere(10.0)
    batteryPack = BatteryPack(batteryCell, ['2p', '6S'])
    print(batteryCell)
    print(liFePoBatteryCell)


    # batteryPack.currentPackVoltage = 2.10 Volts * 6 Series Cells = 12.6 V
    # batteryPack.currentPackAmpere = 10 Amps * 2 Parallel Cells = 20 A
    # batteryPack.currentPackPower = 12.6 V * 20.0 A = 252.0 Watts
    assert tuple(round(v, BatteryPack.SUGGESTED_ROUNDING) for v in batteryPack.current_volts_amps_power) == (12.600, 20.000, 252.000)

    # For battery cell with chemistry AGM if the cell voltage is 2.10 Volts the state of charge is estimated at 55% given datasheets
    assert round(batteryPack.soc, BatteryPack.SUGGESTED_ROUNDING) == 55.000

    # Recharge all 12 cells to 99% equally to give total battery pack state of charge of 99% also
    batteryCell.recharge(99)
    energyCapacityLeftInSingleCell = batteryCell.energy_capacity()                # 99% * 5 Wh = 4.95 Wh
    assert round(batteryPack.soc, BatteryPack.SUGGESTED_ROUNDING) == 99.000
    assert energyCapacityLeftInSingleCell == 4.95

    # batteryPack.currentPackEnergy = 99% soc * 5 Wh * 2 Series Cells * 6 Parallel Cells = 59.4
    assert round(batteryPack.current_pack_energy, BatteryPack.SUGGESTED_ROUNDING) == 59.400


    motor = Consumption("Motor", 24, 0, 1, 10, 50)
    print(motor)

    # Power Draw = 24 V * 1 A = 24 Watts
    assert motor.real_time_power() == 24.000

    # Energy Usage = 24 V * 1 A * 50% * 1 hour = 12 Watt-hours (Wh)
    assert round(motor.real_time_energy(3600), BatteryPack.SUGGESTED_ROUNDING) == 12.000

    # Change current draw: Power Draw = 24 V * 10 A = 240 Watts
    motor.turn_on(Consumption.MAX_POWER_DRAW_MODE)
    assert motor.current == 10
    assert motor.real_time_power() == 240

    # Energy Usage = 24 V * 10 A * 100% * 0.75 hour = 120 Watt-hours (Wh)
    motor.set_duty_cycle(100)
    assert round(motor.real_time_energy(2700), BatteryPack.SUGGESTED_ROUNDING) == 180.000

    try:
        motor.set_duty_cycle(150)
        assert False, "Expected ValueError: Duty cycle must be between 0 and 100"
    except ValueError:
        pass  # test passes

    # Turn off motor and make sure current draw is zero
    motor.turn_off()
    assert motor.deviceOn == False
    assert motor.current == 0.000

    try:
        LED1 = Consumption("RGB LED", 3.3, 0.1, 2, 1, 50)     # 2 amps in NOT less then 1 amp
        LED2 = Consumption("RGB LED", 3.3, 1, 2, 0.5, 50)    # Both 1 amp & 2 amps in NOT less then 0.5 amp
        LED3 = Consumption("RGB LED", 3.3, 0.9, 0, 0.25, 50)  # 0.9 amps in NOT less then 0.25 amps

        assert False, "Expected ValueError: Minimum current draw must be less than average current draw, which must be less than maximum current draw"
    except ValueError:
        pass  # test passes
