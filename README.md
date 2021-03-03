# HOSA

## Abstract

We introduce the Smart Home Security Assistant(HOSA), which uses image recognition AI models to detect the presence ofintruders in the users’ homes. The assistant software constantly receives images captured by a camera and analyzes them. If and only if a personis detected, an alarm is activated and the homeowner is notified aboutthe possible danger. This notification is done with the help of a mobile application, in which the user can check the systems’ current state and also control it. A demo can be found in https://youtu.be/b_f2JWnbJsk .

We describe now the recipe of how to use HOSA.

## Ingredients

- **1 Raspberry Pi**: We use a Raspberry Pi Model B+, to which the camera and the buzzer are attached.
- **1 Camera**: We use a camera of the brand Sain Smart, which is compatible with the Raspberry Pi and is attached to it using a Flexible Flat Cable.
- **1 Buzzer**: The buzzer works as the alarm sound. The model we used LK-Buzzer, from the brand Linkerkit.
- **1 iPhone**: For the user to interact with the system, we created an iOS mobile application. For this reason, we need an Apple’s smartphone.
- **1 Virtual Machine**

## Directions

### 1. In the MBP IoT Platform

For the management of the elements and the connections between them, we used the MBP IoT platform. It is also a open-source platform, whose source code can be found in https://github.com/IPVS-AS/MBP . In the repository you can also found the tutorial of how to use it. After deploying the platform in your machine, creating an account and logging in, you must register the following components in the following order.

1. **Key Pairs**:
In the _Key Pairs_ tab, register the pulic and private RSA key of your VM.
2. **Devices**:
In the _Devices_ tab, register your VM and your Rapspberry Pi. The VM must be linked to its key pair, which you just created. For the creation of the Raspberry Pi, this information don't need to be provided.
3. **Extraction/control Operators**:

4. **Sensors:** In the 

5. **Actuators**:

6. **Rules**:


## Publications
None yet. :( We hope to have one soon though. 