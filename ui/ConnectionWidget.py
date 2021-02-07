from PyQt5.QtWidgets import QFormLayout, QGridLayout, QGroupBox, QLabel, QVBoxLayout, QWidget


class ConnectionWidget(QWidget):
    def __init__(self, hub_client, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._client = hub_client
        self._status_label = QLabel()
        self._device_label = QLabel()

        box = QGroupBox('Connection Status')
        layout = QFormLayout(box)
        layout.addRow('Status:', self._status_label)
        layout.addRow('Device:', self._device_label)

        layout = QVBoxLayout()
        layout.addWidget(box)
        self.setLayout(layout)

        hub_client.events.connection_state_changed += self._on_connection_state_changed

    def _on_connection_state_changed(self, oldstate, newstate):
        self._status_label.setText(newstate.name)
        self._device_label.setText(self._client.connection.name)
