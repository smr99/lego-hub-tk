
from PyQt5 import QtCore
from PyQt5.QtWidgets import QHeaderView, QTableView, QWidget


class PortStatusModel(QtCore.QAbstractTableModel):

    headers = ['Port', 'Device', 'Data']

    def __init__(self, datamodel):
        super(PortStatusModel, self).__init__()
        self._data = datamodel
  
    def refresh(self):
        topleft = self.index(0,1)
        bottomright = self.index(5,2)
        self.dataChanged.emit(topleft, bottomright, [QtCore.Qt.DisplayRole])

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            return PortStatusModel.headers[section]

    def rowCount(self, index):
        return 6

    def columnCount(self, index):
        return 3

    def data(self, index, role):
        if role != QtCore.Qt.DisplayRole: return

        (row, col) = (index.row(), index.column())
        port = row

        if col == 0: return chr(ord('A') + port)
        if col == 1: return self._data.port_device_name(port)
        if col == 2:
            values = self._data.port_device_data(port)
            return ", ".join([str(v) for v in values])


class DevicePortWidget(QTableView):
    def __init__(self, status, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.port_status_model = PortStatusModel(status)

        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.setModel(self.port_status_model)

    def refresh(self):
        self.port_status_model.refresh()

