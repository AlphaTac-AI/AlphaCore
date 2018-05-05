def resolve_data(raw_data, derivatives_prefix):
    derivatives = {}
    if isinstance(raw_data, dict):
        for k, v in raw_data.items():
            if isinstance(v, dict):
                derivatives.update(resolve_data(v, derivatives_prefix + k + '_'))
            elif isinstance(v, list):
                derivatives.update(resolve_data(v, derivatives_prefix + k + '_'))
            else:
                derivatives[derivatives_prefix + k] = v
    elif isinstance(raw_data, list):
        derivatives[derivatives_prefix + 'cnt'] = len(raw_data)
        if len(raw_data) > 1:
            if isinstance(raw_data[0], dict):
                if raw_data[0].keys() == raw_data[1].keys():
                    for ke, va in raw_data[0].items():
                        if isinstance(va, dict):
                            for r in raw_data:
                                derivatives.update(resolve_data(r[ke], derivatives_prefix + ke + '_'))
                        elif isinstance(va, list):
                            for r in raw_data:
                                derivatives.update(resolve_data(r[ke], derivatives_prefix + ke + '_'))
                        elif isinstance(va, (float, int, bool)):
                            derivatives[derivatives_prefix + ke + '_' + 'sum'] = sum([r[ke] for r in raw_data if r[ke]])
                            derivatives[derivatives_prefix + ke + '_' + 'avg'] = float(
                                sum([r[ke] for r in raw_data if r[ke]])) / len(raw_data)
                        else:
                            pass
                else:
                    for li in raw_data:
                        if isinstance(li, dict):
                            derivatives.update(resolve_data(li, derivatives_prefix))
                        elif isinstance(li, list):
                            derivatives.update(resolve_data(li, derivatives_prefix))
                        else:
                            pass
            else:
                pass
        else:
            for li in raw_data:
                if isinstance(li, dict):
                    derivatives.update(resolve_data(li, derivatives_prefix))
                elif isinstance(li, list):
                    derivatives.update(resolve_data(li, derivatives_prefix))
                else:
                    pass
    else:
        derivatives[derivatives_prefix] = raw_data

    return derivatives
