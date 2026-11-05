"""Bounded synthetic operation plans for the interactive live stream."""


def mixed_events(count, job, randomizer, incident_rate):
    events, incidents = [], []
    operation_number = 0
    failures = (
        ("receiver-timeout", "receiver timeout after {} ms"),
        ("device-unavailable", "receiver device unavailable"),
        ("connection-reset", "receiver transport connection reset"),
    )
    while len(events) < count:
        remaining = count - len(events)
        operation = f"live-{job}-{operation_number}"
        request = f"request-{job}-{operation_number}"
        stack = f"stack-{job}-{operation_number}"
        operation_number += 1
        # Reserve all seven positions before selecting an incident. The last
        # few slots use complete normal operations or independent background.
        incident = remaining >= 7 and randomizer.random() < incident_rate
        if incident:
            name, failure = randomizer.choice(failures)
            if name == "receiver-timeout":
                failure = failure.format(randomizer.choice((10, 50, 100)))
            steps = (
                ("OFFLINE", "mock.api", "INFO", "request accepted"),
                ("ONLINE", "mock.receiver", "ERROR", failure),
                ("ONLINE", "mock.processor", "WARNING", "dependency failed; retry 1 scheduled"),
                ("ONLINE", "mock.processor", "ERROR", "dependency retries exhausted after 2 attempts"),
                ("OFFLINE", "mock.pipeline", "ERROR", "operation failed after upstream receiver error"),
                ("ONLINE", "mock.receiver", "NOTICE", "receiver connection restored"),
                ("OFFLINE", "mock.api", "INFO", "operation resumed successfully"),
            )
            incidents.append({"scenario": name, "operation_id": operation,
                              "request_id": request, "start_offset": len(events),
                              "event_count": len(steps)})
        elif remaining >= 4:
            name = "normal"
            steps = (
                ("OFFLINE", "mock.api", "INFO", "request accepted"),
                ("ONLINE", "mock.receiver", "INFO", "receiver sample acquired"),
                ("ONLINE", "mock.processor", "INFO", "sample processed successfully"),
                ("OFFLINE", "mock.api", "INFO", "request completed"),
            )
        else:
            name = "background"
            family = "ONLINE" if len(events) % 2 == 0 else "OFFLINE"
            component = "mock.receiver" if family == "ONLINE" else "mock.api"
            steps = ((family, component, "INFO", "live background sample"),)
        for family, component, severity, message in steps:
            events.append({"family": family, "component": component,
                           "severity": severity, "message": message,
                           "operation_id": operation, "request_id": request,
                           "stack_id": stack, "scenario": name})
    return events, incidents
