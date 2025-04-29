import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QMessageBox,
                            QStackedWidget, QFrame, QSizePolicy)
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5.QtCore import Qt, QSize

from Detector import main_app
from create_classifier import train_classifer
from create_dataset import start_capture

# Global set for storing user names
names = set()

class FaceRecognizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Load existing names
        self.load_names()
        
        # Initialize UI properties
        self.setWindowTitle("Face Recognizer")
        self.setFixedSize(800, 500)
        self.setWindowIcon(QIcon('icon.ico'))
        
        # Initialize stacked widget to handle different pages
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Initialize variables
        self.active_name = None
        self.num_of_images = 0
        
        # Initialize pages
        self.init_home_page()
        self.init_signup_page()
        self.init_login_page()
        self.init_capture_page()
        self.init_recognition_page()
        
        # Show the home page by default
        self.stacked_widget.setCurrentIndex(0)
        
    def load_names(self):
        # Load existing user names from file
        try:
            with open("nameslist.txt", "r") as f:
                x = f.read()
                z = x.rstrip().split(" ")
                for i in z:
                    if i:  # Only add non-empty names
                        names.add(i)
        except FileNotFoundError:
            # Create the file if it doesn't exist
            with open("nameslist.txt", "w") as f:
                pass
    
    def save_names(self):
        # Save names to file before closing
        with open("nameslist.txt", "w") as f:
            for name in names:
                f.write(name + " ")
    
    def init_home_page(self):
        # Create home page widget
        home_page = QWidget()
        
        # Create layout
        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        
        # Add title
        title_label = QLabel("Face Recognition System")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(title_label)
        
        # Add buttons
        signup_btn = QPushButton("Sign Up")
        login_btn = QPushButton("Check a User")
        quit_btn = QPushButton("Quit")
        
        # Style buttons
        for btn in [signup_btn, login_btn, quit_btn]:
            btn.setMinimumSize(200, 50)
            btn.setFont(QFont("Arial", 12))
        
        # Connect buttons to functions
        signup_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        login_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        quit_btn.clicked.connect(self.close)
        
        # Add buttons to layout with spacing
        left_layout.addWidget(signup_btn, alignment=Qt.AlignCenter)
        left_layout.addSpacing(20)
        left_layout.addWidget(login_btn, alignment=Qt.AlignCenter)
        left_layout.addSpacing(20)
        left_layout.addWidget(quit_btn, alignment=Qt.AlignCenter)
        left_layout.addStretch()
        
        # Add image to right side
        image_label = QLabel()
        pixmap = QPixmap('homepagepic.png')
        image_label.setPixmap(pixmap.scaled(400, 400, Qt.KeepAspectRatio))
        image_label.setAlignment(Qt.AlignCenter)
        
        # Add layouts to main layout
        main_layout.addLayout(left_layout, 1)
        main_layout.addWidget(image_label, 1)
        
        # Set layout for home page
        home_page.setLayout(main_layout)
        
        # Add to stacked widget
        self.stacked_widget.addWidget(home_page)
    
    def init_signup_page(self):
        # Create signup page widget
        signup_page = QWidget()
        
        # Create layout
        layout = QVBoxLayout()
        form_layout = QHBoxLayout()
        buttons_layout = QHBoxLayout()
        
        # Add title
        title_label = QLabel("Sign Up")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Add form fields
        name_label = QLabel("Enter your name:")
        name_label.setFont(QFont("Arial", 12))
        self.name_input = QLineEdit()
        self.name_input.setFont(QFont("Arial", 12))
        self.name_input.setMinimumWidth(250)
        
        form_layout.addWidget(name_label)
        form_layout.addWidget(self.name_input)
        layout.addLayout(form_layout)
        
        # Add buttons
        cancel_btn = QPushButton("Cancel")
        next_btn = QPushButton("Next")
        clear_btn = QPushButton("Clear")
        
        # Style buttons
        for btn in [cancel_btn, next_btn, clear_btn]:
            btn.setMinimumSize(120, 40)
            btn.setFont(QFont("Arial", 12))
        
        # Connect buttons to functions
        cancel_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        next_btn.clicked.connect(self.start_training)
        clear_btn.clicked.connect(lambda: self.name_input.clear())
        
        # Add buttons to layout
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(next_btn)
        buttons_layout.addWidget(clear_btn)
        
        # Add buttons layout to main layout
        layout.addSpacing(20)
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        # Set layout for signup page
        signup_page.setLayout(layout)
        
        # Add to stacked widget
        self.stacked_widget.addWidget(signup_page)
    
    def init_login_page(self):
        # Create login page widget
        login_page = QWidget()
        
        # Create layout
        layout = QVBoxLayout()
        form_layout = QHBoxLayout()
        buttons_layout = QHBoxLayout()
        
        # Add title
        title_label = QLabel("Check a User")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Add form fields
        name_label = QLabel("Enter your username:")
        name_label.setFont(QFont("Arial", 12))
        self.login_name_input = QLineEdit()
        self.login_name_input.setFont(QFont("Arial", 12))
        self.login_name_input.setMinimumWidth(250)
        
        form_layout.addWidget(name_label)
        form_layout.addWidget(self.login_name_input)
        layout.addLayout(form_layout)
        
        # Add dropdown for existing users
        self.user_dropdown = QComboBox()
        self.user_dropdown.setFont(QFont("Arial", 12))
        self.user_dropdown.setMinimumWidth(250)
        self.refresh_dropdown()
        layout.addWidget(self.user_dropdown)
        
        # Add buttons
        cancel_btn = QPushButton("Cancel")
        next_btn = QPushButton("Next")
        clear_btn = QPushButton("Clear")
        
        # Style buttons
        for btn in [cancel_btn, next_btn, clear_btn]:
            btn.setMinimumSize(120, 40)
            btn.setFont(QFont("Arial", 12))
        
        # Connect buttons to functions
        cancel_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        next_btn.clicked.connect(self.login)
        clear_btn.clicked.connect(lambda: self.login_name_input.clear())
        
        # Add buttons to layout
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(next_btn)
        buttons_layout.addWidget(clear_btn)
        
        # Add buttons layout to main layout
        layout.addSpacing(20)
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        # Set layout for login page
        login_page.setLayout(layout)
        
        # Add to stacked widget
        self.stacked_widget.addWidget(login_page)
    
    def init_capture_page(self):
        # Create capture page widget
        capture_page = QWidget()
        
        # Create layout
        layout = QVBoxLayout()
        buttons_layout = QHBoxLayout()
        
        # Add title
        title_label = QLabel("Capture Data")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Add image count label
        self.image_count_label = QLabel("Number of images captured = 0")
        self.image_count_label.setFont(QFont("Arial", 14))
        self.image_count_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_count_label)
        
        # Add buttons
        capture_btn = QPushButton("Capture Data Set")
        train_btn = QPushButton("Train The Model")
        
        # Style buttons
        for btn in [capture_btn, train_btn]:
            btn.setMinimumSize(200, 50)
            btn.setFont(QFont("Arial", 12))
        
        # Connect buttons to functions
        capture_btn.clicked.connect(self.capture_images)
        train_btn.clicked.connect(self.train_model)
        
        # Add buttons to layout
        buttons_layout.addWidget(capture_btn)
        buttons_layout.addWidget(train_btn)
        
        # Add buttons layout to main layout
        layout.addSpacing(30)
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        # Set layout for capture page
        capture_page.setLayout(layout)
        
        # Add to stacked widget
        self.stacked_widget.addWidget(capture_page)
    
    def init_recognition_page(self):
        # Create recognition page widget
        recognition_page = QWidget()
        
        # Create layout
        layout = QVBoxLayout()
        buttons_layout = QHBoxLayout()
        
        # Add title
        title_label = QLabel("Face Recognition")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Add buttons
        recognize_btn = QPushButton("Face Recognition")
        home_btn = QPushButton("Go to Home Page")
        
        # Style buttons
        for btn in [recognize_btn, home_btn]:
            btn.setMinimumSize(200, 50)
            btn.setFont(QFont("Arial", 12))
        
        # Connect buttons to functions
        recognize_btn.clicked.connect(self.open_webcam)
        home_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        
        # Add buttons to layout
        buttons_layout.addWidget(recognize_btn)
        buttons_layout.addWidget(home_btn)
        
        # Add buttons layout to main layout
        layout.addSpacing(30)
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        # Set layout for recognition page
        recognition_page.setLayout(layout)
        
        # Add to stacked widget
        self.stacked_widget.addWidget(recognition_page)
    
    def refresh_dropdown(self):
        # Refresh the dropdown with current names
        self.user_dropdown.clear()
        for name in names:
            self.user_dropdown.addItem(name)
    
    def start_training(self):
        # Get the user name from input
        name = self.name_input.text()
        
        # Validate the name
        if not name:
            QMessageBox.critical(self, "Error", "Name cannot be empty!")
            return
        elif name == "None":
            QMessageBox.critical(self, "Error", "Name cannot be 'None'")
            return
        elif name in names:
            QMessageBox.critical(self, "Error", "User already exists!")
            return
        
        # Add name to the set
        names.add(name)
        self.active_name = name
        
        # Refresh dropdown in login page
        self.refresh_dropdown()
        
        # Go to capture page
        self.stacked_widget.setCurrentIndex(3)
    
    def login(self):
        # Get the user name from input or dropdown
        name = self.login_name_input.text()
        
        # If name is empty, get from dropdown
        if not name:
            name = self.user_dropdown.currentText()
        
        # Validate the name
        if not name:
            QMessageBox.critical(self, "Error", "Please enter a name or select from dropdown")
            return
        elif name == "None":
            QMessageBox.critical(self, "Error", "Name cannot be 'None'")
            return
        
        # Set active name
        self.active_name = name
        
        # Go to recognition page
        self.stacked_widget.setCurrentIndex(4)
    
    def capture_images(self):
        # Reset image count
        self.image_count_label.setText("Number of images captured = 0")
        
        # Show instruction
        QMessageBox.information(self, "INSTRUCTIONS", "We will Capture 300 images of your Face.")
        
        # Start capture
        x = start_capture(self.active_name)
        self.num_of_images = x
        
        # Update image count label
        self.image_count_label.setText(f"Number of images captured = {x}")
    
    def train_model(self):
        # Check if enough images are captured
        if self.num_of_images < 300:
            QMessageBox.critical(self, "ERROR", "Not enough Data, Capture at least 300 images!")
            return
        
        # Train the model
        train_classifer(self.active_name)
        
        # Show success message
        QMessageBox.information(self, "SUCCESS", "The model has been successfully trained!")
        
        # Go to recognition page
        self.stacked_widget.setCurrentIndex(4)
    
    def open_webcam(self):
        # Check if active name is set
        if not self.active_name:
            QMessageBox.critical(self, "ERROR", "No active user selected!")
            return
        
        # Open webcam and start face recognition
        main_app(self.active_name)
    
    def closeEvent(self, event):
        # Save names before closing
        self.save_names()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show the main window
    main_window = FaceRecognizerApp()
    main_window.show()
    
    sys.exit(app.exec_()) 