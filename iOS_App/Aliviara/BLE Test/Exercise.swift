//
//  Exercise.swift
//  Aliviara
//
//  Created by Siddharth Vanchinathan on 2/27/16.
//  Copyright © 2016 ACorDiGhaTo. All rights reserved.
//

import Foundation

class Exercise {
    var startDate: NSDate
    var endDate: NSDate
    var sensorData: [[Int]]
    var type: Int
    var success: Bool
    var pain: Bool
    init(type: Int) {
        let now = NSDate()
        
        //Set properties
        self.startDate = now
        self.endDate = now
        self.sensorData = []
        self.type = type
        self.success = false
        self.pain = false
    }
}