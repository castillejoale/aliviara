
//  UARTViewController.swift
//  Adafruit Bluefruit LE Connect
//
//  Created by Collin Cunningham on 9/30/14.
//  Copyright (c) 2014 Adafruit Industries. All rights reserved.
//

import Foundation
import UIKit
import Dispatch
import SwiftHTTP


protocol UARTViewControllerDelegate: HelpViewControllerDelegate {
    
    func sendData(newData:NSData)
    
}


class UARTViewController: UIViewController, UITextFieldDelegate, UITextViewDelegate, MqttManagerDelegate, UIPopoverControllerDelegate {

    enum ConsoleDataType {
        case Log
        case RX
        case TX
    }
    
    enum ConsoleMode {
        case ASCII
        case HEX
    }
    
    //Alejandro
    var currentExercise = Exercise(type: 0)
    //    var sessions = [NSManagedObject]()
    var exercisesValues: NSDictionary?
    var exercisesDescriptions: NSDictionary?
    var exercisesTitles: NSDictionary?
    var exerciseTimer = NSTimer()
    var exercisePlan = [[Int]]()
    var exerciseCounter = 0
    var repetitionCounter = 0
    var lastRead = [Int]()
    var exerciseActive = false
    let tolerance = Float(0.2)
    let messageDelay = 3.0
    let exerciseTime = 10.0
    let repetitions = 3
    
    
    var delegate:UARTViewControllerDelegate?
    @IBOutlet var helpViewController:HelpViewController!
    @IBOutlet weak var consoleView:UITextView!
    @IBOutlet weak var msgInputView:UIView!
    @IBOutlet var msgInputYContraint:NSLayoutConstraint?    //iPad
    @IBOutlet weak var inputField:UITextField!
    @IBOutlet weak var inputTextView:UITextView!
    @IBOutlet weak var consoleCopyButton:UIButton!
    @IBOutlet weak var consoleClearButton:UIButton!
    @IBOutlet weak var consoleModeControl:UISegmentedControl!
    @IBOutlet var sendButton: UIButton!
    @IBOutlet var echoSwitch:UISwitch!
    //Alejandro
    @IBOutlet var echoLabel: UILabel!
    @IBOutlet var exercisesButton: UIButton!
    @IBOutlet var massageButton: UIButton!
    @IBOutlet var exerciseView: UIView!
    @IBOutlet var exerciseImage: UIImageView!
    @IBOutlet var exerciseTitle: UILabel!
    @IBOutlet var exerciseMessage: UILabel!
    @IBOutlet var exerciseDescription: UILabel!
    @IBOutlet var progressView1: UIProgressView!
    @IBOutlet var progressView2: UIProgressView!
    @IBOutlet var progressView3: UIProgressView!
    @IBOutlet var progressView4: UIProgressView!
    @IBOutlet var progressView5: UIProgressView!
    @IBOutlet var progressImage: UIImageView!
    
    private var mqttBarButtonItem : UIBarButtonItem?
    private var mqttBarButtonItemImageView : UIImageView?
    private var mqttSettingsPopoverController:UIPopoverController?
    
    private var echoLocal:Bool = false
    private var keyboardIsShown:Bool = false
    private var consoleAsciiText:NSAttributedString? = NSAttributedString(string: "")
    private var consoleHexText: NSAttributedString? = NSAttributedString(string: "")
    private let backgroundQueue : dispatch_queue_t = dispatch_queue_create("com.adafruit.bluefruitconnect.bgqueue", nil)
    private var lastScroll:CFTimeInterval = 0.0
    private let scrollIntvl:CFTimeInterval = 1.0
    private var lastScrolledLength = 0
    private var scrollTimer:NSTimer?
    private var blueFontDict:NSDictionary!
    private var redFontDict:NSDictionary!
    private var mqttFontDict:NSDictionary!
    private let unkownCharString:NSString = "�"
    private let kKeyboardAnimationDuration = 0.3
    private let notificationCommandString = "N!"
    
    
    convenience init(aDelegate:UARTViewControllerDelegate){
        
        //Separate NIBs for iPhone 3.5", iPhone 4", & iPad
        
        var nibName:NSString
        
        if IS_IPHONE {
            nibName = "UARTViewController_iPhone"
        }
        else{   //IPAD
            nibName = "UARTViewController_iPad"
        }
        
        self.init(nibName: nibName as String, bundle: NSBundle.mainBundle())
        
        self.delegate = aDelegate
        self.title = "UART"
        
    }
    
    
    override func viewDidLoad(){
        
        //setup help view
        self.helpViewController.title = "UART Help"
        self.helpViewController.delegate = delegate
        
        //round corners on console
        self.consoleView.clipsToBounds = true
        self.consoleView.layer.cornerRadius = 4.0
        
        //round corners on inputTextView
        self.inputTextView.clipsToBounds = true
        self.inputTextView.layer.cornerRadius = 4.0

        //retrieve console font
        let consoleFont = consoleView.font
        blueFontDict = NSDictionary(objects: [consoleFont!, UIColor.blueColor()], forKeys: [NSFontAttributeName,NSForegroundColorAttributeName])
        redFontDict = NSDictionary(objects: [consoleFont!, UIColor.redColor()], forKeys: [NSFontAttributeName,NSForegroundColorAttributeName])
        mqttFontDict = NSDictionary(objects: [consoleFont!, UIColor(red: 85/255, green: 85/255, blue: 85/255, alpha: 1)], forKeys: [NSFontAttributeName,NSForegroundColorAttributeName])
    
        //fix for UITextView
        consoleView.layoutManager.allowsNonContiguousLayout = false
        
        // add MQTT button to the navigation bar
        //mqttBarButtonItem = UIBarButtonItem(image: UIImage(named: "mqtt_disconnected"), style: .Plain, target: self, action: "onClickMqtt");
        mqttBarButtonItemImageView = UIImageView(image: UIImage(named: "mqtt_disconnected")!.tintWithColor(self.view.tintColor))      // use a uiimageview as custom barbuttonitem to allow frame animations
        mqttBarButtonItemImageView!.tintColor = self.view.tintColor
        mqttBarButtonItemImageView?.addGestureRecognizer(UITapGestureRecognizer(target: self, action: "onClickMqtt"))
        mqttBarButtonItem = UIBarButtonItem(customView: mqttBarButtonItemImageView!)
        
        self.navigationItem.rightBarButtonItems?.append(mqttBarButtonItem!);
        
        // MQTT init
        let mqttManager = MqttManager.sharedInstance
        if (MqttSettings.sharedInstance.isConnected) {
            mqttManager.delegate = self
            mqttManager.connectFromSavedSettings()
        }
    }
    
    
    deinit {
        let mqttManager = MqttManager.sharedInstance
        mqttManager.disconnect()
    }
    
    
    override func didReceiveMemoryWarning(){
        
        super.didReceiveMemoryWarning()
    
        clearConsole(self)
        
    }
    
    
    override func viewWillAppear(animated: Bool) {
        
        super.viewWillAppear(animated)
        
        //update per prefs
        echoLocal = uartShouldEchoLocal()
        echoSwitch.setOn(echoLocal, animated: false)
        
        //register for keyboard notifications
        NSNotificationCenter.defaultCenter().addObserver(self, selector: Selector("keyboardWillShow:"), name: "UIKeyboardWillShowNotification", object: nil)
        NSNotificationCenter.defaultCenter().addObserver(self, selector: Selector("keyboardWillHide:"), name: "UIKeyboardWillHideNotification", object: nil)
        
        //register for textfield notifications
        //        NSNotificationCenter.defaultCenter().addObserver(self, selector: "textFieldDidChange", name: "UITextFieldTextDidChangeNotification", object:self.view.window)

        // MQTT
        MqttManager.sharedInstance.delegate = self
        updateMqttStatus()
        
        
        //Alejandro
        echoSwitch.hidden = true
        consoleModeControl.hidden = true
        inputTextView.hidden = true
        sendButton.hidden = true
        consoleClearButton.hidden = true
        consoleCopyButton.hidden = true
        msgInputView.hidden = true
        echoLabel.hidden = true
        consoleView.hidden = true
        
        self.fetchExercises()
        self.exerciseView.hidden = true
        // Fetch exercises order
        self.fetchPlan()
        //Initialize visualization
        
//        progressView1.frame =  CGRectMake(progressView1.frame.origin.x , progressView1.frame.origin.y, progressView1.frame.width*1.5, progressView1.frame.height*1.5)
        
        progressView1.transform = CGAffineTransformMakeRotation(CGFloat(M_PI)*(-0.5))
        progressView2.transform = CGAffineTransformMakeRotation(CGFloat(M_PI)*(-0.5))
        progressView3.transform = CGAffineTransformMakeRotation(CGFloat(M_PI)*(-0.5))
        progressView4.transform = CGAffineTransformMakeRotation(CGFloat(M_PI)*(-0.5))
        progressView5.transform = CGAffineTransformMakeRotation(CGFloat(M_PI)*(-0.5))
        
        progressView1.progress = 0.0
        progressView2.progress = 0.0
        progressView3.progress = 0.0
        progressView4.progress = 0.0
        progressView5.progress = 0.0
        
        
        
        

    }
    
    
    override func viewDidAppear(animated: Bool) {
        super.viewDidAppear(animated)
        

    }
    
    
    override func viewDidDisappear(animated: Bool) {
        super.viewDidDisappear(animated)
        
        scrollTimer?.invalidate()
    }
    
    
    override func viewWillDisappear(animated: Bool) {
        
        //unregister for keyboard notifications
        NSNotificationCenter.defaultCenter().removeObserver(self, name: UIKeyboardWillShowNotification, object: nil)
        NSNotificationCenter.defaultCenter().removeObserver(self, name: UIKeyboardWillHideNotification, object: nil)
        
        super.viewWillDisappear(animated)
        
    }
    
    //Alejandro
    @IBAction func pressingExercises(sender: AnyObject) {
        
        if exercisesButton.selected == false {
            exercisesButton.selected = true
            startExercises()
        } else {
            exercisesButton.selected = false
            endExercises()
        }
        
    }
    
    @IBAction func pressingMassage(sender: AnyObject) {
        if massageButton.selected == false {
            massageButton.selected = true
            startMassage()
        } else {
            massageButton.selected = false
            endMassage()
        }
    }
    
    func startMassage() {
        vibrate("StartMassage")
    }
    
    func endMassage() {
        vibrate("EndMassage")
    }
    
    func startExercises() {

        print("Starting exercises")
        self.exerciseView.hidden = false
        
        endMassage()
        
//        print(exercisePlan[0][0])
        self.startExercise(Int(exercisePlan[0][0]))
        

    }
    
    func startExercise(type: Int) {
        
        print("starting exercise " + String(type))
        currentExercise = Exercise(type: type)
        
        let barHeight = Float(0.0)
        progressView1.setProgress(barHeight,animated: true)
        progressView2.setProgress(barHeight,animated: true)
        progressView3.setProgress(barHeight,animated: true)
        progressView4.setProgress(barHeight,animated: true)
        progressView5.setProgress(barHeight,animated: true)
        
        exerciseActive = true
        
        exerciseMessage.text = "Start exercise"
        print("Instructions: " + self.exerciseMessage.text!)
        print(NSDate())

        //Set image
        if let filePath = NSBundle.mainBundle().pathForResource("ex" + String(type), ofType: "jpg"), image = UIImage(contentsOfFile: filePath) {
            exerciseImage.contentMode = .ScaleAspectFit
            exerciseImage.image = image
        } else {
            print("error getting exercise image")
        }

        exerciseCounter++
        repetitionCounter++
        
        //Get exercise key
        let string = "New item - " + "\(type + 1)"
        
        //Set descriptions
        let description = exercisesDescriptions![string]
        exerciseDescription!.text = description as? String

        //Set titles
        let title = exercisesTitles![string]
        exerciseTitle!.text = title as? String

        //Set exercise timer
        exerciseTimer = NSTimer.scheduledTimerWithTimeInterval(exerciseTime, target: self, selector: "terminateTimer", userInfo: nil, repeats: false)
        
    }
    
    func terminateTimer() {
        print("terminateTimer")
        endExercise()
    }
    
    func relax() {
        print("RELAXING, WAITING UNTIL NOT SUCCESS")
        exerciseMessage.text = "Relax"
        print("Instructions: " + self.exerciseMessage.text!)
        print(NSDate())
        
        let barHeight = Float(0.0)
        progressView1.setProgress(barHeight,animated: true)
        progressView2.setProgress(barHeight,animated: true)
        progressView3.setProgress(barHeight,animated: true)
        progressView4.setProgress(barHeight,animated: true)
        progressView5.setProgress(barHeight,animated: true)
        
        
        
        let delay = messageDelay * Double(NSEC_PER_SEC)
        let time = dispatch_time(DISPATCH_TIME_NOW, Int64(delay))
        dispatch_after(time, dispatch_get_main_queue()) {
            print("NOW LETS CONTINUE")
            self.continueExercises()
            
            
            
        }
    }
    
    func endExercise() {
        print("ending exercise")
        
        //Initialize last read
        lastRead = [Int]()
        lastRead.append(-100)
        lastRead.append(-100)
        lastRead.append(-100)
        lastRead.append(-100)
        lastRead.append(-100)
        
        exerciseActive = false
        
        exerciseTimer.invalidate()
        
        let now = NSDate()
        currentExercise.endDate = now
        
        // Send exercise data
        self.sendCurrentExerciseData()
        
        //Check if exercise was succesful
        
        if currentExercise.success == true {
            if self.repetitionCounter >= self.repetitions {
                vibrate("Success")
//                barHeight = Float(1.0)
            }
            
        } else {

            vibrate("Failure")
        }
        
        relax()

    }
    
    
    
    func continueExercises() {
        
        if exerciseCounter < exercisePlan.count {
            
            print("Continuing exercises")
            if currentExercise.success {
                print(repetitionCounter)
                print(repetitions)
                if repetitionCounter >= repetitions{
                    nextExercise()
                } else {
                    repeatExercise()
                }
            } else {
                nextExercise()
            }
            
        } else {
            print("contratulations, you have ended today's exercises")
            endExercises()
        }
        
        
        
        
        
        
    }
    
    func repeatExercise() {
        print("Repeating exercise")
        exerciseMessage.text = "Lets repeat"
        print("Instructions: " + self.exerciseMessage.text!)
        print(NSDate())
        
        //Set exercise timer
        exerciseTimer = NSTimer.scheduledTimerWithTimeInterval(exerciseTime, target: self, selector: "endExercise", userInfo: nil, repeats: false)
        
        exerciseActive = true
        repetitionCounter++
        
    }
    
    func vibrate(type: String) {
        
        print("Vibrating because of: " + type)
        
        var commandType:NSString = ""
        
        if type == "Success"{
            commandType = "s"
        } else if type == "Failure"{
            commandType = "f"
        } else if type == "StartMassage"{
            commandType = "mon"
        } else if type == "EndMassage"{
            commandType = "moff"
        }


        
        if commandType != ""{
            sendUartMessage(commandType, wasReceivedFromMqtt: false)
        }
        
    }
    
    func nextExercise() {
        //Check if there are more exercises left
        print("Next exercise")
        repetitionCounter = 0
        self.startExercise(exercisePlan[exerciseCounter][0])

    }
    
    
    func endExercises() {
        print("Ending exercises")
        self.exerciseView.hidden = true
        exerciseCounter = 0
        exerciseTimer.invalidate()
    }
    
    func sendCurrentExerciseData() {
        
        let interval = Int(currentExercise.endDate.timeIntervalSinceDate(currentExercise.startDate))
        
//        print("Sending the following exercise data")
//        print("Exercise number?")
//        print(currentExercise.type)
//        print("Succeeded?")
//        print(currentExercise.success)
//        print("Reported pain?")
//        print(currentExercise.pain)
//        print("Seconds it took?")
//        print(interval)
        
        //Alejandro
        print("POST")
        
        let stringArray = currentExercise.sensorData.description
        
        var successInt = 0
        if currentExercise.success{
            successInt = 1
        }
        
        var painInt = 0
        if currentExercise.pain{
            painInt = 1
        }
        
        let params:Dictionary<String,AnyObject> = ["exercise": currentExercise.type, "fingers":stringArray,"time": interval,"success": successInt,"pain": painInt]
        
        do {
            let opt = try HTTP.POST("https://3d1606ea.ngrok.io/data", parameters: params)
            opt.start { response in
                if let err = response.error {
                    print("error: \(err.localizedDescription)")
//                    print(response.description)
                    return //also notify app of failure as needed
                }
//                print("opt finished: \(response.description)")
            }
        } catch let error {
            print("got an error creating the request: \(error)")
        }
        
        
    }
    
    func fetchExercises() {
        print("fetching exercises")

        //Get values
        
        if let path = NSBundle.mainBundle().pathForResource("exercisesValues", ofType: "plist") {
            exercisesValues = NSDictionary(contentsOfFile: path)
        }
//        if let dict = exercisesValues {
//            // Use your dict here
//            print(dict)
//        }

        //Get descriptions
        
        if let path = NSBundle.mainBundle().pathForResource("exercisesDescriptions", ofType: "plist") {
            exercisesDescriptions = NSDictionary(contentsOfFile: path)
        }
//        if let dict = exercisesDescriptions {
//            // Use your dict here
//            print(dict)
//            print(dict["New item - 1"]!)
//        }

        
        //Get titles
        
        if let path = NSBundle.mainBundle().pathForResource("exercisesTitles", ofType: "plist") {
            exercisesTitles = NSDictionary(contentsOfFile: path)
        }
//        if let dict = exercisesTitles {
//            // Use your dict here
//            print(dict)
//        }
        
    }
    
    func fetchPlan() {

        print("GET")
        do {
            let opt = try HTTP.GET("https://3d1606ea.ngrok.io/get_plan")
            opt.start { response in
                if let err = response.error {
                    print("error: \(err.localizedDescription)")
                    self.addDefaultPlan()
                    return //also notify app of failure as needed
                } else{
                    
                    ////                    print(response.data)
                    //                    let image: UIImage = UIImage(data: response.data)!
                    //                    self.progressImage.image = image
                    
                    
                    let plan = response.data
//                    print(plan)

                }
//                print("opt finished: \(response.description)")
                //print("data is: \(response.data)") access the response of the data with response.data
            }
        } catch let error {
            print("got an error creating the request: \(error)")
            addDefaultPlan()
        }
        
        addDefaultPlan()

        print("Exercise plan:")
        print(exercisePlan)
    }
    
    func addDefaultPlan() {
        print("Adding default plan")
        exercisePlan.append([0,0])
        exercisePlan.append([1,0])
        exercisePlan.append([2,0])
        exercisePlan.append([4,0])
//        exercisePlan.append([3,0])
//        exercisePlan.append([5,0])
//        exercisePlan.append([10,0])
//        exercisePlan.append([6,0])
//        exercisePlan.append([12,0])
//        exercisePlan.append([7,0])
//        exercisePlan.append([11,0])
//        exercisePlan.append([8,0])
//        exercisePlan.append([9,0])
    }
    
    func updateVisualization() {
        
        if exerciseView.hidden == true {
            return
        }
        
        print("updating visualization")
        
        //Get exercise key
        let string = "New item - " + "\(currentExercise.type + 1)"
        
        //Set descriptions
        let valuesString = exercisesValues![string]!
        let valuesArray = valuesString.componentsSeparatedByString(" ")
        
        var intValues = [Int]()
        for i in 0...valuesArray.count-1 {
            intValues.append(Int(valuesArray[i])!)
        }
        
        let progress1 = min(Float(1 - abs(Float(lastRead[0] - intValues[0])/100.0)) + tolerance,1)
        let progress2 = min(Float(1 - abs(Float(lastRead[1] - intValues[1])/100.0)) + tolerance,1)
        let progress3 = min(Float(1 - abs(Float(lastRead[2] - intValues[2])/100.0)) + tolerance,1)
        let progress4 = min(Float(1 - abs(Float(lastRead[3] - intValues[3])/100.0)) + tolerance,1)
        let progress5 = min(Float(1 - abs(Float(lastRead[4] - intValues[4])/100.0)) + tolerance,1)
        

        progressView1.setProgress(progress1,animated: true)
        progressView2.setProgress(progress2,animated: true)
        progressView3.setProgress(progress3,animated: true)
        progressView4.setProgress(progress4,animated: true)
        progressView5.setProgress(progress5,animated: true)

    }
    
    func checkIfExerciseSucceeded() {
        let totalSum = progressView1.progress + progressView2.progress + progressView3.progress + progressView4.progress + progressView5.progress
        
        if totalSum == 5 {
            print("Success")
            currentExercise.success = true
            self.endExercise()
        } else {
            print("No success yet")
        }
    }
    
    
    @IBAction func reportPain(sender: AnyObject) {
        print("Reporting pain at exercise: " + String(currentExercise.type))
        currentExercise.pain = true
        endExercise()
    }

    @IBAction func viewProgress(sender: AnyObject) {
        print("Viewing progress")
        print("GET")
        do {
            let opt = try HTTP.GET("https://3d1606ea.ngrok.io/get_image")
            opt.start { response in
                if let err = response.error {
                    print("error: \(err.localizedDescription)")
                    return //also notify app of failure as needed
                } else{
                    
////                    print(response.data)
//                    let image: UIImage = UIImage(data: response.data)!
//                    self.progressImage.image = image
                    
                    
                    let getImage =  UIImage(data: response.data)
//                    print(getImage!.size)
                    self.progressImage.image = getImage

                    
                    
                }
//                print("opt finished: \(response.description)")
                //print("data is: \(response.data)") access the response of the data with response.data
            }
        } catch let error {
            print("got an error creating the request: \(error)")
        }
    }
    
    
    func updateConsoleWithIncomingData(newData:NSData) {
        
        //Alejandro
        if exerciseActive == false {
            return
        }
        
        //convert data to string & replace characters we can't display
        let dataLength:Int = newData.length
        var data = [UInt8](count: dataLength, repeatedValue: 0)
        
        newData.getBytes(&data, length: dataLength)
        
        for index in 0...dataLength-1 {
            if (data[index] <= 0x1f) || (data[index] >= 0x80) { //null characters
                if (data[index] != 0x9)       //0x9 == TAB
                    && (data[index] != 0xa)   //0xA == NL
                    && (data[index] != 0xd) { //0xD == CR
                        data[index] = 0xA9
                }
                
            }
        }
        
        
        let newString = NSString(bytes: &data, length: dataLength, encoding: NSUTF8StringEncoding)
        //Alejandro
//        print(newString!)
        var array = newString!.componentsSeparatedByString(" ")
        var indexArray = [Int]()
        var removeCounter = 0

        if array.count > 0 {
            for i in 0...array.count-1 {
                if array[i] == "" {
                    indexArray.append(i)
                }
            }
        }

        if indexArray.count > 0 {
            for j in 0...indexArray.count-1 {
                array.removeAtIndex(indexArray[j] - removeCounter)
                removeCounter++
            }
        }

        if array.count == 5{
            
            lastRead = [Int]()
            
            for i in 0...array.count-1 {
                lastRead.append(Int(array[i])!)
            }
            
            //FLIP ARRAY
            lastRead = lastRead.reverse()
            
//            print("We got all data points")
//            print(lastRead)
            updateVisualization()
            checkIfExerciseSucceeded()
            
            //Add data points
            currentExercise.sensorData.append(lastRead)
            

        }
//            printLog(self, funcName: "updateConsoleWithIncomingData", logString: newString! as String)

        
        

    }
    
    

    
    

    @IBAction func clearConsole(sender : AnyObject) {
        
        consoleView.text = ""
        consoleAsciiText = NSAttributedString()
        consoleHexText = NSAttributedString()
        
    }
    
    
    @IBAction func copyConsole(sender : AnyObject) {
        
        let pasteBoard = UIPasteboard.generalPasteboard()
        pasteBoard.string = consoleView.text
        let cyan = UIColor(red: 32.0/255.0, green: 149.0/255.0, blue: 251.0/255.0, alpha: 1.0)
        consoleView.backgroundColor = cyan
        
        UIView.animateWithDuration(0.45, delay: 0.0, options: UIViewAnimationOptions.CurveEaseIn, animations: { () -> Void in
            self.consoleView.backgroundColor = UIColor.whiteColor()
        }) { (finished) -> Void in
            
        }
        
    }
    
    
    @IBAction func sendMessage(sender:AnyObject){
        
//        sendButton.enabled = false
        
//        if (inputField.text == ""){
//            return
//        }
//        let newString:NSString = inputField.text
        
        //Alejandro
//        if (inputTextView.text == ""){
//            return
//        }
//        let newString:NSString = inputTextView.text
        let newString:NSString = "Hola!"
        
        
     
        sendUartMessage(newString, wasReceivedFromMqtt: false)
        
//        inputField.text = ""
        inputTextView.text = ""
        
      
        
    }
    
    
    
    func sendUartMessage(message: NSString, wasReceivedFromMqtt: Bool) {
        // MQTT publish to TX
        let mqttSettings = MqttSettings.sharedInstance
        if(mqttSettings.isPublishEnabled) {
            if let topic = mqttSettings.getPublishTopic(MqttSettings.PublishFeed.TX.rawValue) {
                let qos = mqttSettings.getPublishQos(MqttSettings.PublishFeed.TX.rawValue)
                MqttManager.sharedInstance.publish(message as String, topic: topic, qos: qos)
            }
        }
        
        // Send to uart
        if (!wasReceivedFromMqtt || mqttSettings.subscribeBehaviour == .Transmit) {
            let data = NSData(bytes: message.UTF8String, length: message.length)
            delegate?.sendData(data)
        }
        
    }
    
    
    @IBAction func echoSwitchValueChanged(sender:UISwitch) {
        
        let boo = sender.on
        uartShouldEchoLocalSet(boo)
        echoLocal = boo
        
    }
    
    
    func receiveData(newData : NSData){
        
        if (isViewLoaded() && view.window != nil) {
            // MQTT publish to RX
            let mqttSettings = MqttSettings.sharedInstance
            if(mqttSettings.isPublishEnabled) {
                if let message = NSString(data: newData, encoding: NSUTF8StringEncoding) {
                    if let topic = mqttSettings.getPublishTopic(MqttSettings.PublishFeed.RX.rawValue) {
                        let qos = mqttSettings.getPublishQos(MqttSettings.PublishFeed.RX.rawValue)
                        MqttManager.sharedInstance.publish(message as String, topic: topic, qos: qos)
                    }
                }
            }
            
            // Update UI
            updateConsoleWithIncomingData(newData)
        }
        
    }
    
    
    func keyboardWillHide(sender : NSNotification) {
        
        if let keyboardSize = (sender.userInfo?[UIKeyboardFrameBeginUserInfoKey] as? NSValue)?.CGRectValue() {
            
            let yOffset:CGFloat = keyboardSize.height
            let oldRect:CGRect = msgInputView.frame
            msgInputYContraint?.constant += yOffset
            
            if IS_IPAD {
                let newRect = CGRectMake(oldRect.origin.x, oldRect.origin.y + yOffset, oldRect.size.width, oldRect.size.height)
                msgInputView.frame = newRect    //frame animates automatically
            }
         
            else {
                
                let newRect = CGRectMake(oldRect.origin.x, oldRect.origin.y + yOffset, oldRect.size.width, oldRect.size.height)
                msgInputView.frame = newRect    //frame animates automatically
                
            }
            
            keyboardIsShown = false
            
        }
        else {
//            printLog(self, funcName: "keyboardWillHide", logString: "Keyboard frame not found")
        }
        
    }
    
    
    func keyboardWillShow(sender : NSNotification) {
    
        //Raise input view when keyboard shows
    
        if keyboardIsShown {
            return
        }
    
        //calculate new position for input view
        if let keyboardSize = (sender.userInfo?[UIKeyboardFrameBeginUserInfoKey] as? NSValue)?.CGRectValue() {
            
            let yOffset:CGFloat = keyboardSize.height
            let oldRect:CGRect = msgInputView.frame
            msgInputYContraint?.constant -= yOffset     //Using autolayout on iPad
            
//            if (IS_IPAD){
            
                let newRect = CGRectMake(oldRect.origin.x, oldRect.origin.y - yOffset, oldRect.size.width, oldRect.size.height)
                self.msgInputView.frame = newRect   //frame animates automatically
//            }
//            
//            else {  //iPhone
//             
//                var newRect = CGRectMake(oldRect.origin.x, oldRect.origin.y - yOffset, oldRect.size.width, oldRect.size.height)
//                self.msgInputView.frame = newRect   //frame animates automatically
//                
//            }
            
            keyboardIsShown = true
            
        }
        
        else {
//            printLog(self, funcName: "keyboardWillHide", logString: "Keyboard frame not found")
        }
    
    }
    
    
    //MARK: UITextViewDelegate methods
    
    func textViewShouldBeginEditing(textView: UITextView) -> Bool {
        
        if textView === consoleView {
            //tapping on consoleview dismisses keyboard
            inputTextView.resignFirstResponder()
            return false
        }
        
        return true
    }
    
    
//    func textViewDidEndEditing(textView: UITextView) {
//        
//        sendMessage(self)
//        inputTextView.resignFirstResponder()
//        
//    }
    
    
    //MARK: UITextFieldDelegate methods
    
    func textFieldShouldReturn(textField: UITextField) ->Bool {
        
        //Keyboard's Done button was tapped
        
//        sendMessage(self)
//        inputField.resignFirstResponder()

        
        return true
    }
    
    
    @IBAction func consoleModeControlDidChange(sender : UISegmentedControl){
        
        //Respond to console's ASCII/Hex control value changed
        
        switch sender.selectedSegmentIndex {
        case 0:
            consoleView.attributedText = consoleAsciiText
            break
        case 1:
            consoleView.attributedText = consoleHexText
            break
        default:
            consoleView.attributedText = consoleAsciiText
            break
        }
        
    }
    
    
    func didConnect(){
    
        
    }
    
    
    func sendNotification(msgString:String) {
        
        let note = UILocalNotification()
//        note.fireDate = NSDate().dateByAddingTimeInterval(2.0)
//        note.fireDate = NSDate()
        note.alertBody = msgString
        note.soundName =  UILocalNotificationDefaultSoundName
        
        dispatch_async(dispatch_get_main_queue(), { () -> Void in
            UIApplication.sharedApplication().presentLocalNotificationNow(note)
        })
        
        
    }

    
    // MARK: - MQTT
    
    
    func onClickMqtt() {
        let mqqtSettingsViewController = MqttSettingsViewController(nibName: "MqttSettingsViewController", bundle: nil)

        if (IS_IPHONE) {
            self.navigationController?.pushViewController(mqqtSettingsViewController, animated: true)
        }
        else if (IS_IPAD) {
            mqttSettingsPopoverController?.dismissPopoverAnimated(true)
            
            mqttSettingsPopoverController = UIPopoverController(contentViewController: mqqtSettingsViewController)
            mqttSettingsPopoverController?.delegate = self
            mqqtSettingsViewController.view.backgroundColor = UIColor.darkGrayColor()
            mqqtSettingsViewController.preferredContentSize = CGSizeMake(400, 0)
            
            let aFrame:CGRect = mqttBarButtonItem!.customView!.frame
            mqttSettingsPopoverController?.presentPopoverFromRect(aFrame,
                inView: mqttBarButtonItem!.customView!.superview!,
                permittedArrowDirections: UIPopoverArrowDirection.Any,
                animated: true)
        }
            }
    
    func updateMqttStatus() {
        if let imageView = mqttBarButtonItemImageView {
            let status = MqttManager.sharedInstance.status
            let tintColor = self.view.tintColor
            
            switch (status) {
            case .Connecting:
                let imageFrames = [
                    UIImage(named:"mqtt_connecting1")!.tintWithColor(tintColor),
                    UIImage(named:"mqtt_connecting2")!.tintWithColor(tintColor),
                    UIImage(named:"mqtt_connecting3")!.tintWithColor(tintColor)
                ]
                imageView.animationImages = imageFrames
                imageView.animationDuration = 0.5 * Double(imageFrames.count)
                imageView.animationRepeatCount = 0;
                imageView.startAnimating()
                
            case .Connected:
                imageView.stopAnimating()
                imageView.image = UIImage(named:"mqtt_connected")!.tintWithColor(tintColor)
                
            default:
                imageView.stopAnimating()
                imageView.image = UIImage(named:"mqtt_disconnected")!.tintWithColor(tintColor)
            }
        }
    }
    
    // MARK: MqttManagerDelegate
    
    func onMqttConnected() {
        dispatch_async(dispatch_get_main_queue(), { [unowned self] in
            self.updateMqttStatus()
            })
    }
    
    func onMqttDisconnected() {
        dispatch_async(dispatch_get_main_queue(), { [unowned self] in
            self.updateMqttStatus()
            })
    }
    
    func onMqttMessageReceived(message : String, topic: String) {
        dispatch_async(dispatch_get_main_queue(), { [unowned self] in
            self.sendUartMessage((message as NSString), wasReceivedFromMqtt: true)
            })
    }
    
    func onMqttError(message : String) {
        let alert = UIAlertController(title:"Error", message: message, preferredStyle: UIAlertControllerStyle.Alert)
        alert.addAction(UIAlertAction(title: "Ok", style: UIAlertActionStyle.Default, handler: nil))
        self.presentViewController(alert, animated: true, completion: nil)
    }
    
    // MARK: UIPopoverControllerDelegate
    
    func popoverControllerDidDismissPopover(popoverController: UIPopoverController) {
        // MQTT
        MqttManager.sharedInstance.delegate = self
        updateMqttStatus()
    }

}





