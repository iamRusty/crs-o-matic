# $Id$
#
# htmltable - part of the CRS-o-matic project
# Copyright (C) 2003  Joe Pasko
# Copyright (C) 2008  Darwin M. Bautista
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
This module and its sole class, HTMLTable, is based on version 1.13 of
the PyHtmlTable class and module written by Joe Pasko (http://pasko.net/PyHtmlTable/).
"""

import sys
import re

from nxnarray import NxNArray


class HTMLTable(object):

    """A Pythonic interface for HTML table manipulation and generation

    The tables generated by HTMLTable is XHTML 1.0-compliant.
    """

    def __init__(self, rows, cols, tattr=None):
        self.htcells = NxNArray(rows, cols, '&nbsp;')
        self.tabattr = '' # Holds border=FOO, color=bar pairs
        self.cellattr = {} # <td . $attr  (row,col) tuple
        self.endcellattr = {} # $attr . </td>
        self.colattr = {}
        self.rowattr = {} # <tr = $attr indexed by row
        self.celltype = {} # th, td indexed by (row,col) tuple
        self.celldefattrs = ''
        # On data insertion, should we append or overwrite cell attributes?
        # Defaults to append.
        self.overwriteattrs = False
        self.maxRow = self.htcells.rows
        self.maxCol = self.htcells.cols
        self.defctype = 'td'
        self.spantext = '<!-- spanned cell -->'
        # Handle table attrs if passed in
        if tattr is not None:
            self.setTableattrs(tattr)

    def setCellDefattrs(self, indict):
        """Sets default attributes for cells in table
           Used if cell does not have specific atributes
        """

        for key, val in indict.iteritems():
            newattr = '%s="%s"' % (key, val)
            self.celldefattrs = "".join([self.celldefattrs, newattr])

    def getCellDefattrs(self):
        """Returns default cell attributes"""

        return self.celldefattrs

    def clearCellDefattrs(self):
        """Clears default cell attributes"""

        self.celldefattrs = None

    def add_array_to_row(self, row, col, inarr, attrs=None):
        """Adds list of data specified by inarr to table object
          starting at row,col

          Optionally specify attributes to set on cells being added
          by defining the attrs dictionary

          Note: Cell attribute insertion can be additive or overwriting depending
                on calls to setReplaceCellattrs() or setAppendCellattrs()

                Default is to append new attributes
        """

        arlen = len(inarr)
        for i in range(arlen):
            self.setCellcontents(row, col + i, inarr[i], attrs)

    def add_array_to_col(self, row, col, inarr, attrs=None):
        """Adds list of data specified by inarr to table object
          starting at row,col

          Optionally specify attributes to set on cells being added
          by defining the attrs dictionary

          Note: Cell attribute insertion can be additive or overwriting depending
                on calls to setReplaceCellattrs() or setAppendCellattrs()

                Default is to append new attributes
        """

        arlen = len(inarr)
        for i in range(arlen):
            self.setCellcontents(row + i, col, inarr[i], attrs)

    def setCellColSpan(self, row, col, numcells):
        """Sets colSPAN starting at rowidx, colidx
           spanning numcells
           (Remember rows,cols start at 0,0)
        """

        for i in range(col + 1, col + numcells):
            self.setCellcontents(row, i, self.spantext)
        self.setCellattrs(row, col, {'colspan': numcells})

    def setCellRowSpan(self, row, col, numcells):
        """Sets rowSPAN starting at rowidx, colidx
           spanning numcells
           (Remember rows,cols start at 0,0)
        """

        for i in range(row + 1, row + numcells):
            self.setCellcontents(i, col, self.spantext)

        self.setCellattrs(row, col, {'rowspan': numcells})

    def __dumpattrs(self, indict):
        print "\n\n----dumping generic attrs ----"
        print indict
        print "\n\n"

    def __start_row(self, row):
        ratter = self.getRowattrs(row)
        if ratter:
            trow = ''.join(['<tr ', str(ratter), '>'])
        else:
            trow = '<tr>'
        return trow

    def __end_row(self):
        return '</tr>'

    def __end_table(self):
        return '</table>'

    def setColattrs(self, col, indict):
        """Presently unused"""

        # print "INdexs out of range"
        if col >= self.maxCol:
            return None
        for key, val in indict.iteritems():
            if self.colattr.has_key(col):
                pval = self.colattr[col]
                self.colattr[col] = '%s %s="%s"' % (pval, key, val)
            else:
                self.colattr[col] = '%s="%s"' % (key, val)

    def setRowattrs(self, row, indict):
        """Sets attributes for give rowidx

           indict is a dictionary of key=val pairs
           {'bgcolor':'black'} translates to <tr BGcolOR=\"BLACK\">

        """

        # print "INdexs row out of range"
        if row >= self.maxRow:
            return None
        for key, val in indict.iteritems():
            if self.rowattr.has_key(row):
                pval = self.rowattr[row]
                self.rowattr[row] = '%s %s="%s"' % (pval, key, val)
            else:
                self.rowattr[row] = '%s="%s"' % (key, val)

    def getRowattrs(self, row):
        """ Returns attribute string for given rowidx which
            was set by setRowattrs
        """

        return self.rowattr[row] if self.rowattr.has_key(row) else None

    def getColattrs(self, col):
        """Presently unused"""

        return self.colattr[col] if self.colattr.has_key(col) else None

    def getCellattrs(self, row, col):
        """Returns attributes set for specific cell at rowidx colidx """

        return self.cellattr[(row, col)] if self.cellattr.has_key((row, col)) else None

    def __getendCellattrs(self, row, col):
        """Presently unused"""

        return self.endcellattr[(row, col)] if self.endcellattr.has_key((row, col)) else None

    def __setendCellattrs(self, row, col, indict):
        """Presently unused"""

        # print "INdexs out of range"
        if row >= self.maxRow or col >= self.maxCol:
            return None
        for key, val in indict.iteritems():
            if self.endcellattr.has_key((row, col)):
                pval = self.endcellattr[(row, col)]
                self.endcellattr[(row, col)] = '%s %s="%s"' % (pval, key, val)
            else:
                self.endcellattr[(row, col)] = '%s="%s"' % (key, val)

    def setCellattrs(self, row, col, indict):
        """ Sets cell attributes for cell at rowidx, colidx

            indict is a dictionary of key=val pairs

           {'bgcolor':'black', 'width':200} yields

           <td BGcolOR=\"BLACK\" width=\"200\" >
           on output
        """

        # print "INdexs out of range"
        if row >= self.maxRow or col >= self.maxCol:
            return None
        if self.overwriteattrs:
            self.clearCellattrs(row, col)
        for key, val  in indict.iteritems():
            if self.cellattr.has_key((row, col)):
                pval = self.cellattr[(row, col)]
                self.cellattr[(row, col)] = '%s %s="%s" ' % (pval, key, val)
            else:
                self.cellattr[(row, col)] = '%s="%s" ' % (key, val)

    def setTableattrs(self, indict):
        """ Sets table attributes in <table directive

            indict is a dictionary of key=val pairs
            {'width':'800','border':2,'bgcolor':'green'} yields

            <table WIDth=\"800\" BORDER=\"2\" BGcolOR=\"GREEN\">
        """

        for key, val in indict.iteritems():
            tpair = ' %s="%s"' % (key, val)
            self.tabattr = self.tabattr + tpair

    def setCelltype(self, row, col, ctype='td'):
        """ Celltypes can be td or th """

        # print "INdexs out of range"
        if row >= self.maxRow or col >= self.maxCol:
            return None
        self.celltype[(row, col)] = ctype

    def getCelltype(self, row, col):
        """Returns Celltypes which is td or th"""

        # print "INdexs out of range"
        if row >= self.maxRow or col >= self.maxCol:
            return None
        if self.celltype.has_key((row, col)):
            return self.celltype[(row, col)]
        else:
            return 'td'

    def setReplaceCellattrs(self):
        """After calling this function calls to setCellattrs() will
        append attribute information to cells

        If the cell had attributes width=\"400\", after calling this
        function calls to setCellattrs( x, y, {'bgcolor':'black'})
        yields attributes for cell x,y of:

                bgcolor=\"black\"

        """

        self.overwriteattrs = True

    def setAppendCellattrs(self):
        """After calling this function calls to setCellattrs() will
        append attribute information to cells

        If the cell had attributes width=\"400\", after calling this
        function calls to setCellattrs( x, y, {'bgcolor':'black'})
        yields attributes for cell x,y of:

                 width=\"400\" bgcolor=\"black\"

        Note: This is the default behavior

        """

        self.overwriteattrs = False

    def setCellcontents(self, row, col, data, attrs=None):
        """Puts data into cell at rowidx, colidx
           Takes optional attribute dictionary for cell
        """

        # Force casting as a string
        if data or data is not None:
            data = str(data)
        else:
            data = '&nbsp;'

        self.htcells.set_cell(row, col, data)

        # May have need to grow the table in the NxNArray class
        # Query class to reset max row/cols if necessary
        self.maxRow = self.htcells.rows
        self.maxCol = self.htcells.cols

        if attrs is not None:
            if self.overwriteattrs:
                self.clearCellattrs(row, col)
            self.setCellattrs(row, col, attrs)

    def clearCellattrs(self, row, col):
        """ Clear cells attributes """

        if not self.cellattr.has_key((row, col)):
            return None
        del self.cellattr[(row, col)]

    def clearRowattrs(self, row):
        """ Clear row attributes """

        if not self.rowattr.has_key(row):
            return None
        del self.rowattr[row]

    def clearTableattrs(self):
        """ Clear Table attributes """

        self.tabattr = ''

    def getCellcontents(self, row, col):
        """ Get cells stored data values
            Return an &nbsp if cell is None
        """

        retstr = self.htcells.get_cell(row, col)
        if retstr is None:
            return '&nbsp;'
        else:
            return retstr

    def getmaxRow(self):
        """Returns index of highest row( number_of_rows -1 )"""

        return self.maxRow - 1

    def getmaxCol(self):
        """Returns index of highest col( number_of_cols -1 )"""

        return self.maxCol - 1

    def __start_table(self):
        if self.tabattr:
            stag = '<table%s>' % self.tabattr
            return stag
        else:
            return '<table>'

    def __has_only_rowcolsp_attrs(self, attrstr):

        if attrstr is None or not attrstr:
            return False

        colpat = re.compile('colspan="\w+', re.IGNORECASE)
        rowpat = re.compile('rowspan="\w+', re.IGNORECASE)
        multieqpat = re.compile('.*=.*=')

        if not re.match(colpat, attrstr) and not re.match(rowpat,
                attrstr):
            return False  # we didn't have colspan or rowspan at all

        if not re.match(multieqpat, attrstr):
            return True

               # We've got two equals, now check to see if any left
               # After we nuke colspan and rowspan

        attrstr = re.sub(colpat, '', attrstr)
        attrstr = re.sub(rowpat, '', attrstr)
        if re.match('.*=.*', attrstr):  # We have some other attribute left over
            return False
        return True

    def __resCell(self, row, col):
        data = self.getCellcontents(row, col)

        # Must be a spanned cell, don't print anything

        if data == self.spantext:
            return None
        ctype = self.getCelltype(row, col)
        cattr = self.getCellattrs(row, col)
        ceattr = self.__getendCellattrs(row, col)
        cdefattr = self.getCellDefattrs()
        closetag = '</%s>' % ctype

        if cattr is not None:

            # If we only have a single rowspan/colspan attribute, merge it with
            # the default cell attributes IF NO OthER ATtrIBUTES EXIST FOR thAT CELL

            if cdefattr and self.__has_only_rowcolsp_attrs(cattr):
                retstr = '<%s %s>' % (ctype, cdefattr + ' ' + cattr)
            else:
                retstr = '<%s %s>' % (ctype, cattr)
        elif cdefattr:
            retstr = '<%s %s>' % (ctype, str(cdefattr))
        else:
            retstr = '<%s>' % ctype
        retstr = retstr + str(data)  # Add the meat of the cell

        # Process closing tags

        if ceattr is not None:
            retstr = retstr + ceattr + closetag
        else:
            retstr = retstr + closetag
        return retstr

    # Run through the cells and adjust the tuple indexes down

    def __adjust_dbl_indx_dict_rows_down(self, indict,
            add_after_this_row):
        for i in range(self.maxRow, add_after_this_row, -1):
            for key, val in indict.iteritems():
                (row, col) = (int(key[0]), int(key[1]))
                if row != i:
                    continue

                indict[(row + 1, col)] = val

                del indict[(row, col)]

    def add_row(self, row):
        """ Adds row to table after specified rowidx.
            Adding row at rowidx -1 adds row to top of table """

        if row > self.maxRow:
            row = self.maxRow

        # Update attrs for rowattr, cellattr, then call
        # array updater,

        if row != self.maxRow - 1:  # Adding row to bottom, no need to move attrs
            self.__adjust_dict_rows_down(self.rowattr, row)

            self.__adjust_dbl_indx_dict_rows_down(self.cellattr, row)
            self.__adjust_dbl_indx_dict_rows_down(self.celltype, row)

        self.__adjust_2d_array_rows_down(self.htcells, row)

    def add_col(self, col):
        """ Adds col to table after specified colidx
            Adding col at colidx -1 adds col to left of table
        """

        if col > self.maxCol:
            col = self.maxCol

        # Update attrs for colattr, cellattr, then call
        # array updater,

        if col != self.maxCol - 1:  # If Adding col to right,skip moving attrs

            self.__adjust_dict_cols_right(self.rowattr, col)
            self.__adjust_dbl_indx_dict_cols_right(self.cellattr, col)
            self.__adjust_dbl_indx_dict_cols_right(self.celltype, col)

        self.__adjust_2d_array_cols_right(self.htcells, col)

    # Run through the cells and adjust the tuple index down

    def __adjust_dict_rows_down(self, indict, add_after_this_row):

        if add_after_this_row == self.maxRow - 1:
            return

        if add_after_this_row == -1:

            for i in range(self.maxRow, 0, -1):
                if indict.has_key(i - 1):
                    val = indict[i - 1]
                    indict[i] = val
                    del indict[i - 1]
            return

        for i in range(self.maxRow, add_after_this_row, -1):
            if indict.has_key(i - 1):
                val = indict[i - 1]
                indict[i] = val
                del indict[i - 1]

    def __adjust_dict_cols_right(self, indict, add_after_this_col):
        if add_after_this_col == self.maxCol - 1:
            return
        if add_after_this_col == -1:
            for i in range(self.maxCol, 0, -1):
                if indict.has_key(i - 1):
                    val = indict[i - 1]
                    indict[i] = val
                    del indict[i - 1]
            return

        for i in range(self.maxCol, add_after_this_col, -1):
            if indict.has_key(i - 1):
                val = indict[i - 1]
                indict[i] = val
                del indict[i - 1]

    def __adjust_dbl_indx_dict_cols_right(self, indict,
            shift_after_this_col):
        for i in range(self.maxCol, shift_after_this_col, -1):
            for key, val in indict.iteritems():
                (row, col) = (int(key[0]), int(key[1]))
                if col != i:
                    continue

                indict[(row, col + 1)] = val
                del indict[(row, col)]

    def __adjust_2d_array_rows_down(self, inarr, add_after_this_row):

        self.maxRow = inarr.get_num_rows()
        self.maxCol = inarr.get_num_cols()

        deffill = self.htcells.fill

        # Adding to bottom, no need to move data

        if self.maxRow - 1 == add_after_this_row:

            i = self.maxRow

            for j in range(self.maxCol):

                inarr.set_cell(i, j, deffill)

            self.maxRow = self.htcells.rows
            self.maxCol = self.htcells.cols

            return

        for i in range(self.maxRow, add_after_this_row + 1, -1):

            for j in range(self.maxCol):
                data2mv = inarr.get_cell(i - 1, j)
                inarr.set_cell(i, j, data2mv)
                inarr.set_cell(i - 1, j, deffill)
                self.maxRow = self.htcells.rows
                self.maxCol = self.htcells.cols

    def __adjust_2d_array_cols_right(self, inarr, add_after_this_col):

        self.maxRow = inarr.get_num_rows()
        self.maxCol = inarr.get_num_cols()

        deffill = self.htcells.fill

        # Adding cols to right edge no need for data moving

        if self.maxCol - 1 == add_after_this_col:

            i = self.maxCol

            for j in range(self.maxRow):

                inarr.set_cell(j, i, deffill)

            self.maxRow = self.htcells.rows
            self.maxCol = self.htcells.cols

            return

        # Shift data

        for i in range(self.maxCol, add_after_this_col + 1, -1):
            for j in range(self.maxRow):
                data2mv = inarr.get_cell(j, i - 1)
                inarr.set_cell(j, i, data2mv)
                inarr.set_cell(j, i - 1, deffill)

        self.maxRow = self.htcells.rows
        self.maxCol = self.htcells.cols

    def display(self):
        """ Prints html table """

        ts = self.__start_table()
        print ts
        for row in range(self.maxRow):
            tr = self.__start_row(row)
            trc = self.__end_row()
            print tr
            for col in range(self.maxCol):
                td = self.__resCell(row, col)
                if td:
                    print td
            print trc, '\n'

        print self.__end_table()
        sys.stdout.flush()

    def return_html(self):
        """ Returns html table as string """

        htmltbl = []
        ts = self.__start_table()
        htmltbl.append(ts)

        for row in range(self.maxRow):
            tr = self.__start_row(row)
            trc = self.__end_row()
            htmltbl.append(tr)
            for col in range(self.maxCol):
                td = self.__resCell(row, col)
                if td: # Spanned cells return None
                    htmltbl.append(td)
            htmltbl.append("".join([trc, '\n']))
        htmltbl.append("".join([self.__end_table(), '\n\n']))
        return "".join(htmltbl)


def main():
    print "Content-Type: text/html\n\n"
    print """<html><head></head><body bgcolor="white"> """

    print '<b> 2 by 2 table</b> '

    t = HTMLTable(2, 2, {'width': '400', 'border': 2, 'bgcolor': 'white'})

    t.setCellcontents(0, 0, 'T1 Cell 00')
    t.setCellcontents(0, 1, 'T1 Cell 01')
    t.setCellcontents(1, 0, 'T1 Cell 01')
    t.setCellcontents(1, 1, 'T1 Cell 11')

    t.setCellattrs(0, 0, {'bgcolor': 'red', 'width': 100})
    t.setCellattrs(1, 1, {'bgcolor': 'red'})
    t.display()

    print """<b>Dynamically grow outside initial table boundaries by setting
                cells outside current boundaries </b>"""

    t.setCellcontents(2, 0, 'T1 Cell 20') # Grow outside initial bounds
    t.setCellcontents(2, 1, 'T1 Cell 21')
    t.display()

    print '<p><b> Explicitly add row after row index 1 </b>'

    t.add_row(1) # Add a row after row index 1
    t.display()

    print '<p><b> Explicitly adding col after column index 1 </b>'

    t.add_col(1) # Add a col after col index 1
    t.display()

    print '<hr><b> AFTER  row and col SPANNING </b>'
    t.setCellRowSpan(1, 0, 2)  # Span cell at index row 1,col 0, make 2 high
    t.setCellColSpan(1, 1, 2)  # colSpan cell at index row 1, col 1, make 2 wide

    t.display()

    print '<hr><b> Embed in new table </b>'

    htmlstr = t.return_html()

    nt = HTMLTable(1, 4, {'width': '800', 'border': 2, 'bgcolor': 'green'})
    nt.setCellcontents(0, 0, 'Cell th....text left')
    nt.setCellcontents(0, 1, 'Text right')
    nt.setCellcontents(0, 2, htmlstr)
    nt.setCellattrs(0, 0, {'bgcolor': 'blue', 'width': 200, 'align': 'left'})
    nt.setCellattrs(0, 1, {'width': 200, 'align': 'right'})
    nt.setCelltype(0, 0, 'th')
    nt.display()
    print '</body></html>'


if __name__ == "__main__":
    main()
