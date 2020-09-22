from datetime import datetime
import json

simple = dict(int_list=[1, 2, 3],

              text='string',

              number=3.44,

              boolean=True,

              none=None)


class A(object):

    def __init__(self, simple):

        self.simple = simple

    def __eq__(self, other):

        if not hasattr(other, 'simple'):
            return False

        return self.simple == other.simple

    def __ne__(self, other):

        if not hasattr(other, 'simple'):
            return True

        return self.simple != other.simple


complex = dict(a=A(simple), when=datetime(2016, 3, 7))


class CustomEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime):
            return {'__datetime__': o.replace().isoformat()}

        return {f'__{o.__class__.__name__}__': o.__dict__}


def decode_object(o):
    if '__A__' in o:

        a = A()

        a.__dict__.update(o['__A__'])

        return a

    elif '__datetime__' in o:

        return datetime.strptime(o['__datetime__'], '%Y-%m-%dT%H:%M:%S')

    return o


serialized = json.dumps(complex, indent=4, cls=CustomEncoder)
deserialized = json.loads(serialized, object_hook=decode_object)


print(serialized)
print(deserialized)