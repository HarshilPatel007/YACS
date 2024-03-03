from PySide6 import QtWidgets


class WelcomeDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Welcome to YACS!")
        self.setFixedSize(500, 150)

        self.play_as_human_radio_white = None
        self.play_as_human_radio_black = None
        self.fischer_random_checkbox = None
        self.setup_layout()

    def setup_layout(self):
        player_selection_layout = QtWidgets.QHBoxLayout()

        white_groupbox = self.create_player_groupbox("White")
        black_groupbox = self.create_player_groupbox("Black")

        self.fischer_random_checkbox = QtWidgets.QCheckBox("Use Fischer Random aka chess960")

        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        player_selection_layout.addWidget(white_groupbox)
        player_selection_layout.addWidget(black_groupbox)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.fischer_random_checkbox)
        main_layout.addLayout(player_selection_layout)
        main_layout.addWidget(button_box)

        self.setLayout(main_layout)

    def create_player_groupbox(self, color):
        groupbox = QtWidgets.QGroupBox()
        groupbox.setTitle(color)

        play_as_human_radio = QtWidgets.QRadioButton("Human")
        play_as_engine_radio = QtWidgets.QRadioButton("Engine")
        play_as_human_radio.setChecked(True)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(play_as_human_radio)
        layout.addWidget(play_as_engine_radio)

        groupbox.setLayout(layout)

        if color == "White":
            self.play_as_human_radio_white = play_as_human_radio
        else:
            self.play_as_human_radio_black = play_as_human_radio

        return groupbox

    def get_options(self):
        white_play_as = (
            "human" if self.play_as_human_radio_white.isChecked() else "engine"
        )
        black_play_as = (
            "human" if self.play_as_human_radio_black.isChecked() else "engine"
        )
        is_fischer_random = self.fischer_random_checkbox.isChecked()

        return {
            "white_play_as": white_play_as,
            "black_play_as": black_play_as,
            "is_fischer_random": is_fischer_random,
        }
