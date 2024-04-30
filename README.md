Project Proposal: https://docs.google.com/document/d/11qA_jg-LfylxA3p2fgLPwpKuj3B_QRrEaa22cD1DsPU/edit

# SQR Web Application

This project centers around the development of a certificate-based QR code generator and scanner, prioritizing security through public and private key encryption. By utilizing this approach, the application aims to effectively validate QR codes, mitigating the risks associated with QR code phishing, or "quishing".

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Acknowledgements](#acknowledgements)

## Project Overview

The SQR (Secure QR) Web Application is designed to address the growing concern of QR code security in various contexts, including authentication, access control, and data integrity. By leveraging certificate-based encryption techniques, the application ensures that QR codes can be reliably verified, minimizing the risk of unauthorized access or manipulation.

## Features

- **Certificate-Based Encryption**: Utilizes public and private key encryption to generate and validate QR codes, enhancing security and trust.
- **QR Code Generation**: Allows users to create encrypted QR codes containing sensitive information securely.
- **QR Code Scanning**: Provides a robust scanning mechanism to verify the authenticity and integrity of QR codes.
- **User Authentication**: Implements user authentication to control access to QR code generation and scanning functionalities.


## Getting Started

### Prerequisites

Before installing the SQR Web Application, ensure that you have the following prerequisites:

- python (version 10 or above)


### Installation

1. **Clone the Repository**: 
   ```bash
   git clone https://github.com/username/sqr-web-app.git
   ```

2. **Navigate to the Project Directory**:
   ```bash
   cd sqr-web-app
   ```

3. **Install Dependencies**:
   ```bash
   brew install zbar
   pip install requirements.txt
   ```


5. **Start the Application**:
   ```bash
   python3 run.py
   ```

## Usage

Once the SQR Web Application is up and running, users can perform the following actions:

1. **Generate QR Codes**:
   - Generate the QR code securely using certificate-based encryption.

2. **Scan QR Codes**:
   - Utilize the scanner to capture SQR codes securely.
   - Automatically verify the authenticity and integrity of scanned QR codes.
   - Learn the link and user associated with a SQR code.


## Acknowledgements

The development of the SQR Web Application was made possible through the contributions and support of the following individuals:

Emeka Ezike, Victor Goncalves, Gianni Hernadez-De la Pena, Boluwaji Odufuwa

We extend our sincere gratitude to all those who have helped in shaping and improving this project.
