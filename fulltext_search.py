from sqlalchemy.sql.expression import ColumnElement
from sqlalchemy.ext.compiler import compiles
from sqlalchemy import text


class Match(ColumnElement):
    def __init__(self, columns, value, mode=''):
        try:  # hacky way to see if columns is a list of columns or just one column
            [_ for _ in columns]  # noqa
            self.columns = columns
        except NotImplementedError:
            self.columns = [columns]
        print(type(self.columns))
        self.value = text(value)
        self.mode = mode


@compiles(Match)
def _match(element, compiler, **kw):
    print(f'''
    MATCH ({''.join(compiler.process(c, **kw) for c in element.columns)})
    AGAINST("{compiler.process(element.value)}")
    ''')
    return f'''
    MATCH ({''.join(compiler.process(c, **kw) for c in element.columns)})
    AGAINST("{compiler.process(element.value)}")
    '''
