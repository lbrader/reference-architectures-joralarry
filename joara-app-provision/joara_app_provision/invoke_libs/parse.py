from .splitter import unquote




def parse_extra_vars(extra_vars_opt):
    extra_vars = {}
    extra_vars.update(parse_kv_by_comma(extra_vars_opt))
    return extra_vars

def parse_kv_by_comma(args):
    ''' convert a string of key/value items to a dict '''
    options = {}
    if args is not None:
        try:
            vargs = args.split(",")
        except ValueError as ve:
            if 'no closing quotation' in str(ve).lower():
                raise Exception("error parsing argument string, try quoting the entire line.")
            else:
                raise
        for x in vargs:
            if "=" in x:
                k, v = x.split("=", 1)
                options[k.strip()] = unquote(v.strip())
    return options

