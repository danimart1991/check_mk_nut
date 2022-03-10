from .agent_based_api.v1 import *


def discover_nut(section):
    section = clean_section(section)
    for ups_name, variable, _ in section:
        yield Service(item=title_generator(ups_name, variable))


def check_nut(item, section):
    section = clean_section(section)
    for ups_name, variable, value in section:
        if title_generator(ups_name, variable) == item:
            if variable == "Load":
                yield from check_load(value)
                return
            if variable == "Output Voltage":
                yield from check_output_voltage(value)
                return
            else:
                yield Result(state=State.OK, summary=value)
                return


def check_load(value):
    value = int(value)
    value_warn = 50
    value_crit = 70
    yield Metric("load", value, levels=(value_warn, value_crit))

    state = State.OK
    if value >= value_crit:
        state = State.CRIT
    elif value >= value_warn:
        state = State.WARN
    yield Result(state=state, summary=f"Load on UPS: {render.percent(value)}")


def check_output_voltage(value):
    value = float(value)
    value_warn = 245
    value_crit = 250
    yield Metric("output_voltage", value, levels=(value_warn, value_crit))

    state = State.OK
    if value >= value_crit:
        state = State.CRIT
    elif value >= value_warn:
        state = State.WARN
    yield Result(state=state, summary=f"Output Voltage: {value} V")


def clean_section(section):
    items = []
    for line in section:
        variable = line[1][:-1]
        if (variable == "ups.load"):
            variable = "Load"
        elif (variable == "output.voltage"):
            variable = "Output Voltage"
        items.append([line[0], variable, ' '.join(line[2:])])
    return items


def title_generator(upsname, variable):
    return f"{upsname} - {variable}"


register.check_plugin(
    name="nut",
    service_name="NUT %s",
    discovery_function=discover_nut,
    check_function=check_nut,
)
