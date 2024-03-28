# Badgerd Device Initialization Manager 

BDIM is multi platform application to initialize [Badgerd-Embedded](https://github.com/Badger-Embedded) devices automatically. It supports Windows and Linux platforms. BDIM is aiming to listen and detect USB devices that detected by OS and run sub process commands to initialize the device asynchronously. BDIM needs Badgerd initialize commands for instance BDIM is using the sd-mux-ctrl command line tool to initialize  [SDWireC](https://badgerd.nl/sdwirec/#quick-start)

Thanks to [pyudev](https://pyudev.readthedocs.io/en/latest/#documentation ), [janus](https://github.com/aio-libs/janus)  and [WMI](https://github.com/tjguk/wmi) to make the life easy for me! 

BDIM is aiming make the initialization process for Badgerd-Devices, but the usage and purpose can be generalized. Because the structure is independent between USB devices and subprocess commands. 

## Requirements: 
Usage is as simple as watching TV (well, it depends I know). Basically you need to clone the repo
* Run the below commands for dependencies: 
    - python3 -m venv .venv (**Recommended)
    - source .venv/bin/activate(**Recommended)
    - pip install poetry (!if you don't have)
    - poetry install (It will install all required dependencies according to your OS)

* You need to have Badgerd sd-mux-ctrl for SDWireC initialization:
    - Follow the steps on [QuickStart Page](https://badgerd.nl/sdwirec/#quick-start)
## Usage:
Simply run the below command on the terminal:
- badgerd-dim
It will ask you basic questions, I choose the SDWireC for below example:
```
Please choose the device you want to initialize and press Enter:
 Badgerd SDWireC: 1,
 Badgerd USB Mux: 2

1
Please enter a number to start initilization with it: 
308
````

And now you can simply watch it, of course you need to plug in your USB device to initialize.  Below log part can be example for SDWireC initialization. 
```
Initialization is starting, please don't remove the device until initilization is done
Initialization is done, new serial id will become bdgrd_sdwirec_307
```
If you attach the device after initialization it will run the validate and test coroutines.  It is a basic test for write operations on SD Card partition. 
```
Please validate below info if the device is correct
Badgerd SDWireC is found Number of FTDI devices found: 1
Dev: 0, Manufacturer: SRPOL, Serial: bdgrd_sdwirec_303, Description: sd-wire

/dev/sda1
test is starting
--ts test is running
/dev/sda1
create test file
test file was created successfully in ts mode

test file removed successfully
```

you can repeat these operation until you tired because of plug in and plug out. When you want to quit the program just press Ctrl+C, it will terminate BDIM. 
