# HOSA

## Abstract

We introduce the Smart Home Security Assistant (HOSA), which uses image recognition AI models to detect the presence ofintruders in the users’ homes. The assistant software constantly receives images captured by a camera and analyzes them. If and only if a personis detected, an alarm is activated and the homeowner is notified aboutthe possible danger. This notification is done with the help of a mobile application, in which the user can check the systems’ current state and also control it. A video demo can be found [here](https://youtu.be/b_f2JWnbJsk).

## What you will need

### Hardware

- **1 Raspberry Pi**: We use a Raspberry Pi Model B+, to which the camera and the buzzer are attached;
- **1 Camera**: We use a camera of the brand Sain Smart;
- **1 Buzzer**: The buzzer works as the alarm sound. The model we used LK-Buzzer, from the brand Linkerkit;
- **1 iPhone**: For the user to interact with the system, we created an iOS mobile application. For this reason, we need an Apple’s smartphone.

### Sofware

- **1 Virtual Machine**;

### Accounts

- **Account in Heroku** (Free);
- **Apple Developer Account** (U$ 99/ year);
  This is necessary because HOSA iOS app uses Universal Links and Push Notifications.

## Directions

### 1. Pre-Configurations

1. Connect the Buzzer to the Raspberry Pi in the logical port 15. For that, we used a shield;
2. Connect the Camera to the Raspberry Pi. For that, we used a Flexible Flat Cable;
3. Enable the Camera: `sudo raspi-config` -> Interfacing Options -> Camera -> Yes

### 2. The Heroku Platform

We created a server for handling all the requests related to the token generation feature. It is hosted in the cloud platform Heroku and enables the persistent storage of all tokens. We chose to use Heroku for the facility to deploy a webserver using HTTPS. This protocol is necessary for enabling Universal Links.

- Create an account in [heroku website](https://www.heroku.com/) in case you don't have it yet;
- Install Heroku in your local machine following the [official guide](https://devcenter.heroku.com/articles/heroku-cli#download-and-install);
- Go to the location of `Authorization` folder of this repository in your local machine;
- Go to the file `apple-app-site-association` and change the `appID` key's value to be team-ID.bundle-ID of your mobile application. It will be something as `"HXBS8U8294.johnAppleseed.Hosa"`. Your team ID and Bundle Identifier you can find in the `Signing and Capabilities` tab of HOSA's mobile application. This step is necessary to enable the Universal Links;
- Deploy it to Heroku with Git. You can follow [this tutorial](https://devcenter.heroku.com/articles/git);
- If you execute `git remote -v` command in the terminal in the same folder, you should obtain something like 
  `https://git.heroku.com/hidden-sea-1234.git (fetch)`;
  
  The part between the .com/ and .git is the ID of your server. In the following steps, we are going to need your Heroku's domain name, which is its ID followed by `.herokuapp.com`, such as `hidden-sea-1234.herokuapp.com`.

### 3. The iOS Platform

In order to allow the users to control HOSA and access its state, we built an iOS mobile application. Execute the following steps in order to use it.

1. Clone the [source repository](https://github.com/lauracorssac/HOSA-iOS) to your machine;
2. In the file `DataManager.swift` change the variable `raspberryIP` to be the IP of your Raspberry Pi. Change `vmIP` to be the IP of your VM and `herokuPath` to be your heroku domain name;
3. In order to allow the Universal Linking to take place, go to the `Signing and Capabilities` tab of your XCode project and in the `Associated Domains` capability, add something like the following:

    `applinks:your-heroku-domain`
  
    Note you must replace `your-heroku-domain` by your actual Heroku domain, which is something like `hidden-sea-1234.herokuapp.com`.
	
4. Generate a `.p8` certificate to allow sending push notifications to a real device and also silent push notifications. To do so, head over to Apple Developer Member Center and log in. 
  	* There, go to Certificates, Identifiers & Profiles and then Keys;
  	* Tap the plus button to generate a new key;
  	* Select Apple Push Notifications service (APNs) to enable it and name it something like "Push Notification Key";
  	* Then, continue and you will have your `.p8` certificate, which you can download to use it later. It will have a name like `AuthKey_4SVKWF123R.p8`. The 4SVKWF123R part of the file name is the Key ID. You’ll also need this. More information you can find in [this tutorial](https://www.raywenderlich.com/11395893-push-notifications-tutorial-getting-started).

### 4. The MBP IoT Platform

For the management of the elements and the connections between them, we used the MBP IoT platform. It is also a open-source platform, whose source code can be found in [this repository](https://github.com/IPVS-AS/MBP). In the repository you can also found the tutorial of how to use it. After deploying the platform in your machine, creating an account and logging in, you must register the following components in the following order.
		
* ####  **Key Pairs**:
  In the _Key Pairs_ tab, register the pulic and private RSA key of your VM.

* ####  **Devices**:
  In the _Devices_ tab, register your VM and your Rapspberry Pi. The VM must be linked to its key pair, which you just created. For the creation of the Raspberry Pi, this information don't need to be provided.

* #### **Extraction/Control Operators**: 

  In the _Extraction/Control Operators_ tab, we register the following five items. For all of them, the field "Parameters" should be left empty and the field "Unit" should have the value "No Unit".
  
    <details>
      <summary>Camera Operator</summary>

  1. Open the _Camera_ folder of this repo;

  2. In the `TokenValidationManager.py` file, change the value of the `YOUR_HEROKU_URL` variable to be the URL of your webserver hosted in Heroku;

  3. Go back to MBP and register a new Operator. There will be a new form and in its _Operator scripts_ section, you must upload all the files inside _Camera Operator_ folder.
    </details>

    <details>
      <summary>Buzzer Commands Operator</summary>
  
  1. Open the _Buzzer Commands_ folder of this repository;

  2. In the `TokenValidationManager.py` file, change the value of the `YOUR_HEROKU_URL` variable to be the URL of your webserver hosted in Heroku;

  3. In the `NotificationManager.py` file, change the value of the `HOST` variable to be the IP of your VM. Change the `BUNDLE_ID` and `TEAM_ID` to be the your's Apple Developer information. Both Bundle ID and Team ID can be found in the `Signing and Capabilities` tab in Xcode. Change the `APNS_KEY_ID` to be the Key ID generated in section 3.4. Change `APNS_AUTH_KEY_PATH` to be the full name of your key. Something like `AuthKey_4SVKWF123R.p8`. Change also the `DEVICE_TOKEN` variable to be the token of your iPhone. When you run the application, this value will be printed by the following function in your `AppDelegate.swift` file;

    ```swift
    func application( _ application: UIApplication, didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data) {
      let tokenParts = deviceToken.map { data in String(format: "%02.2hhx", data) }
      let token = tokenParts.joined()
      print("Device Token: \(token)")
    }
    ````
    
  4. Place your `.p8` certificate generated in previously in this folder;

  5. Go back to MBP and register a new Operator. There will be a new form and in its _Operator scripts_ section, you must upload all the files inside _Buzzer Commands Operator_ folder.

    </details>

  <details>
  <summary>System Commands Operator</summary>
  
  1. Open the _System Commands_ folder of this repository;

  2. Follow steps 2, 3 and 4 of _Buzzer Commands Operator_;

  3. Go back to MBP and register a new Operator. There will be a new form and in its _Operator scripts_ section, you must upload all the files inside _System Commands Operator_ folder.
  </details>

  <details>
    <summary>Notification Operator</summary>
  
  1. Open the _Notification_ folder of this repository;

  2. Follow the steps 2,3 and 4 of the _Buzzer Commands Operator_;

  3. Go back to MBP and register a new Operator. There will be a new form and in its _Operator scripts_ section, you must upload all the files inside _Notification Operator_ folder.
  </details>

  <details>
    <summary>Buzzer Operator</summary>

    1. Open the _Buzzer_ folder of this repository;

    2. In the `mbp_client.py` file, change the value of the `YOUR_VM_IP` variable to be the IP of your VM;

    3. Go back to MBP and register a new Operator. There will be a new form and in its _Operator scripts_ section, you must upload all the files inside _Buzzer Operator_ folder.
  </details>

* #### **Sensors:** 

  In the _Sensors_ tab, you must register the following three items.

  <details>
    <summary>Camera Sensor</summary>

    * The _Sensor Type_ should be _Camera_;

    * The _Extraction Operator_ should be the _Camera Operator_;

    * The _Device_ should be the Raspberry Pi.
  </details>

  <details>
    <summary>System Commands Sensor</summary>

    * The _Sensor Type_ should be _Touch_;

    * The _Extraction Operator_ should be the _System Commands Operator_;

    * The _Device_ should be the VM.
  </details>

  <details>
    <summary>Buzzer Commands Sensor</summary>

    * The _Sensor Type_ should be _Touch_;

    * The _Extraction Operator_ should be the _Buzzer Commands Operator_;

    * The _Device_ should be the VM.
  </details>

* #### **Actuators**: 
  In the _Actuators_ tab, you must register the following two items.

  <details>
    <summary>Notification Actuator</summary>

    * The _Actuator Type_ may be _Vibration_;

    * The _Control Operator_ should be the _Notification Operator_;

    * The _Device_ should be the VM.
  </details>

  <details>
    <summary>Buzzer Actuator</summary>

    * The _Actuator Type_ may be _Buzzer_;

    * The _Control Operator_ should be the _Buzzer Operator_;

    * The _Device_ should be the Raspberry Pi.
  </details>

* #### **Rules**: 
  The _Rules_ tab is divided in the following three sub-tabs.

* #### **Rule Actions**: 

  In the _Rule Actions_ tab, you must register the following two items.

  <details>
    <summary>Buzzer Action</summary>
  
  * For _Action Type_ select _Actuator Action_;

  * For _Actuator_ select _Buzzer Actuator_;

  * For _suffix_ type "action".
  </details>

  <details>
    <summary>Notification Action</summary>
  
  * For _Action Type_ select _Actuator Action_;

  * For _Actuator_ select _Notification Actuator_;

  * For _suffix_ type "action".
  </details>

* #### **Rule Conditions**: 

  In the _Rule Conditions_ tab, you must register the following two items.

  <details>
    <summary>Camera + System Commands</summary>
  
  * Name it Camera + System Commands. Proceed;

  * Drag the _Camera_ and the _System Commands_ sensors to the indicated place and add an _or_ Operator between them; Proceed;

  * Make sure the pattern is 

    ```
    SELECT * FROM pattern [every (
    event_0= <camera_sensor_ID> OR 
    event_1= <system_commands_sensor_ID>
    )]
    ```
  </details>

  <details>
    <summary> Camera + System Commands + Buzzer Commands</summary>

    * Name it Camera + System Commands + Buzzer Commands. Proceed;

    * Drag the _Camera_, the _System Commands_, and the _Buzzer Commands_ sensors to the indicated place and add two _or_ Operators between them. Proceed;

    * Make sure the pattern is 

    ```
    SELECT * FROM pattern [every (
    event_0= <camera_sensor_ID> OR 
    event_1= <system_commands_sensor_ID> OR
    event_2= <buzzer_commands_sensor_ID>
    )]
    ```

  </details>

* #### **Rule Definitions**: 

  In the _Rule Definitions_ tab, you must register the following two items.

  <details>
    <summary> Camera + System Commands -> Notification</summary>

    * For _Condition_ select _Camera + System Commands_;

    * For _Action_ select _Notification Action_.

  </details>

  <details>
    <summary> Camera + System Commands + Buzzer Commands -> Buzzer</summary>

    * For _Condition_ select _Camera + System Commands + Buzzer Commands_;

    * For _Action_ select _Buzzer Action_.

  </details> 

## How to use

  1. Go to the MBP platform and start all the five operators deployed;
  2. For first use, generate a token. For that, execute the `FirstTokenManager.py` in your local machine. Copy the token printed in the terminal;
  3. Update your heroku server by executing `git add .` -> `git commit -m "First token generation"` -> `git push heroku master`;
  4. Run the mobile application and paste the token in the _Token Validation_ screen.
