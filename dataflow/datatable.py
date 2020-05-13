from beautifultable import BeautifulTable, Style, NoStyle, BoxStyle
from beautifultable.compat import to_unicode
from bs4 import BeautifulSoup
from dataflow import localization as loc



class SubTableStyle(NoStyle):
    column_separator_char = '|'
    header_separator_char = '─'



class ConsoleTable(BeautifulTable):

    def __init__(self, *args, **kwargs):
        super(ConsoleTable, self).__init__(*args, **kwargs)
        self._title = None
        self.title_bottom_char = '─'


    @property
    def title(self): return self._title

    @title.setter
    def title(self, value): self._title = value


    def get_string(self, recalculate_width=True):
        """Get the table as a String.

        Parameters
        ----------
        recalculate_width : bool, optional
            If width for each column should be recalculated(default True).
            Note that width is always calculated if it wasn't set
            explicitly when this method is called for the first time ,
            regardless of the value of `recalculate_width`.

        Returns
        -------
        str:
            Table as a string.
        """
        # Empty table. returning empty string.
        if len(self._table) == 0:
            return ''

        if self.serialno and self.column_count > 0:
            self.insert_column(0, self.serialno_header,
                               range(1, len(self) + 1))

        # Should widths of column be recalculated
        if recalculate_width or sum(self._column_widths) == 0:
            self._calculate_column_widths()

        string_ = []

        # Drawing the top border
        if self.top_border_char:
            string_.append(
                self._get_top_border())


        # Drawing title
        if self._title is not None and len(self._title) > 0:
            table_width = self.get_table_width()
            padding = table_width - len(self.title) - len(self.left_border_char) - len(self.right_border_char)
            lpad = int(padding / 2)
            rpad = padding - lpad
            content = self.left_border_char + ' ' * lpad + self._title  + ' ' * rpad + self.right_border_char
            if len(self.title_bottom_char) > 0:
                content += '\n'
                len_lr_char = len(self.intersect_header_left) + len(self.intersect_header_right)
                content += self.intersect_header_left + self.title_bottom_char * (table_width - len_lr_char) + self.intersect_header_right

            string_.append(content)



        # Print headers if not empty or only spaces
        if ''.join(self._column_headers).strip():
            headers = to_unicode(self._column_headers)
            string_.append(headers)

            if self.header_separator_char:
                string_.append(
                    self._get_header_separator())

        # Printing rows
        first_row_encountered = False
        for row in self._table:
            if first_row_encountered and self.row_separator_char:
                string_.append(
                    self._get_row_separator())
            first_row_encountered = True
            content = to_unicode(row)
            string_.append(content)

        # Drawing the bottom border
        if self.bottom_border_char:
            string_.append(
                self._get_bottom_border())

        if self.serialno and self.column_count > 0:
            self.pop_column(0)

        return '\n'.join(string_)



class DataTable(object):
    def __init__(self, title='', headers=None, rows=None):
        self._title = title
        self._headers = headers or []
        self._rows = rows or []


    @property
    def title(self): return self._title

    @title.setter
    def title(self, value): self._title = value


    @property
    def headers(self): return self._headers

    @headers.setter
    def headers(self, value): self._headers = value

    @property
    def rows(self): return self._rows

    @property
    def num_columns(self):
        ncol = 0
        for r in self._rows: ncol = max(ncol, len(r))
        return ncol



    def __getitem__(self, item): return self._rows[item]

    def __setitem__(self, key, value): self._rows[key] = value


    def add_row(self, row): self._rows.append(row)


    def render_to_string(self,
                         words=None,
                         style=BoxStyle, substyle=SubTableStyle):

        def create_console_table(dt, subtable):
            # set style
            t = ConsoleTable(max_width=1e6)
            t.set_style(Style.STYLE_NONE)
            cur_style = substyle if subtable else style
            for k, v in cur_style.__dict__.items():
                if k.startswith('__'): continue
                if not hasattr(t, k): continue
                setattr(t, k, v)


            # title
            t.title = dt.title

            # headers
            if len(dt.headers) > 0:
                t.column_headers = dt.headers

            for i in range(len(dt.rows)):
                row = dt.rows[i]
                items = []
                for v in row:
                    if isinstance(v, DataTable):
                        it = create_console_table(v, True)
                        items.append(it)
                    else:
                        items.append(v)

                t.append_row(items)

            return t

        dt = self.translate(words, miss_error=False)
        t = create_console_table(dt, False)
        return str(t)




    def render_to_html(self,
                       words=None):

        soup = BeautifulSoup('', 'html.parser')

        def create_html_table(dt):
            table = soup.new_tag('table')

            # title
            if dt.title is not None and len(dt.title) > 0:
                tr = soup.new_tag('tr')
                table.append(tr)
                td = soup.new_tag('td', attrs={'colspan': dt.num_columns})
                tr.append(td)
                td.string = dt.title



            # header
            if len(dt.headers) > 0:
                tr = soup.new_tag('tr')
                table.append(tr)
                for c in dt.headers:
                    td = soup.new_tag('td')
                    tr.append(td)
                    td.string = c

            # rows
            for i in range(len(dt.rows)):
                row = dt.rows[i]
                tr = soup.new_tag('tr')
                table.append(tr)

                for v in row:
                    td = soup.new_tag('td')
                    tr.append(td)

                    if not isinstance(v, DataTable):
                        td.string = str(v)
                    else:
                        inner_table = create_html_table(v)
                        td.append(inner_table)

            return table

        dt = self.translate(words, miss_error=False)
        t = create_html_table(dt)

        return t.prettify()



    def translate(self, words, miss_error=True):

        def __translate(dt):
            title = loc.translate(dt.title, words, miss_error)
            headers = [loc.translate(h, words, miss_error) for h in dt.headers]
            rows = []
            for row in dt.rows:
                items = []
                for v in row:
                    if isinstance(v, DataTable):
                        items.append(__translate(v))
                    elif isinstance(v, str):
                        items.append(loc.translate(v, words, miss_error))
                    else:
                        items.append(v)

                rows.append(items)

            return DataTable(title=title, headers=headers, rows=rows)

        return __translate(self)