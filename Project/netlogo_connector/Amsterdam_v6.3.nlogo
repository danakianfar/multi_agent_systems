__includes [ "agents.nls" ]
breed [bus_stops bus_stop]
undirected-link-breed [routes route]
breed [buses bus]

bus_stops-own [
  name
  passengers_waiting
  passengers_that_arrived
]

routes-own [
  route_size
]

globals [
  amsterdam_bus_stops_names
  days
  hours
  minutes
  current_time
  passengers
  average_waiting_time
  average_travelling_time
  expenses
  amount_passengers_waiting
  number_of_messages
  bus_type1_price
  bus_type1_cost_per_patch
  bus_type1_capacity
  bus_type2_price
  bus_type2_cost_per_patch
  bus_type2_capacity
  bus_type3_price
  bus_type3_cost_per_patch
  bus_type3_capacity
  general_action_cost
  leasing_list
  average_travelling_time_remaining
  final_average_travelling_time
]

to setup
  clear-all
  reset-ticks
  setup-statistics
  set-time
  create-world
  get-daily-ridership-schedule
  update-bus-stops
  setup-costs
  add-bus 1
end

to calculate-average-travelling-time
  let sum_temp 0
  let list_temp filter [(item 8 ? != -1) or (item 7 ? != -1) or (item 6 ?)] passengers
  foreach list_temp [
    ifelse days < 2
    [
      set sum_temp sum_temp + item 5 ?
    ]
    [
      ifelse not item 6 ?
      [
        set sum_temp (sum_temp + item 5 ? + 180)
      ]
      [
        set sum_temp (sum_temp + item 5 ?)
      ]
    ]
  ]
  if length list_temp > 0 [
    set final_average_travelling_time (sum_temp / length list_temp)
  ]
end

to setup-statistics
  set expenses 0
  set average_waiting_time 0
  set average_travelling_time 0
  set amount_passengers_waiting 0
  set number_of_messages 0
  set final_average_travelling_time 0
end

to update-passengers-statistics
  calculate-average-travelling-time
  let total_waiting_time 0
  let total_travelling_time 0
  set amount_passengers_waiting 0
  let pos 0
  foreach passengers [
    if (item 8 ? != -1) or (item 7 ? != -1) [
      let arrived? item 6 ?
      let ride_duration item 5 ?
      let waiting_time item 4 ?
      let b_s item 8 ?
      if not arrived? [
        set ride_duration ride_duration + 1
        if (b_s != -1) [
          set waiting_time waiting_time + 1
        ]
      ]
      set ? replace-item 5 ? ride_duration
      set ? replace-item 4 ? waiting_time
      set passengers replace-item pos passengers ?
    ]
    set total_waiting_time total_waiting_time + item 4 ?
    set total_travelling_time total_travelling_time + item 5 ?
    if (not item 6 ?) and (item 8 ? != -1) and (item 7 ? = -1) [
      set amount_passengers_waiting amount_passengers_waiting + 1
    ]
    set pos pos + 1
  ]
  let n filter [(item 8 ? = -1) and (item 7 ? = -1) and item 6 ?] passengers
  let n2 filter [(item 8 ? != -1) or (item 7 ? != -1) and not item 6 ?] passengers

  let sum_temp 0
  foreach n [
    set sum_temp sum_temp + item 5 ?
  ]

  if (length n > 0) [
    set average_waiting_time (total_waiting_time / length n)
    set average_travelling_time (sum_temp / length n)
  ]

  let sum_temp2 0
  foreach n2 [
    set sum_temp2 sum_temp2 + item 5 ?
  ]
  if (length n2 > 0) [
    set average_travelling_time_remaining (sum_temp2 / length n2)
  ]
end

to setup-costs
  set bus_type1_capacity 12
  set bus_type1_price 6000
  set bus_type1_cost_per_patch 1
  set bus_type2_capacity 60
  set bus_type2_price 12000
  set bus_type2_cost_per_patch 1.5
  set bus_type3_capacity 150
  set bus_type3_price 20000
  set bus_type3_cost_per_patch 2
end

to create-world
  ;World's max-pxcor and max-pycor: 40,30.
  import-drawing "amsterdam-new-map.png"
  create-bus-stops
end

to create-bus-stops
  set amsterdam_bus_stops_names ["Amstel" "Amstelveenseweg" "Buikslotermeer" "Centraal" "Dam"
    "Evertsenstraat" "Floradorp" "Haarlemmermeerstation" "Hasseltweg" "Hendrikkade"
    "Leidseplein" "Lelylaan" "Muiderpoort" "Museumplein" "RAI" "SciencePark" "Sloterdijk"
    "Surinameplein" "UvA" "VU" "Waterlooplein" "Weesperplein" "Wibautstraat" "Zuid"]

  let xs [27 11 31 22 21 11 25 11 26 25 17 4 31 17 19 35 6 10 38 14 23 24 25 15]
  let ys [7 4 30 21 18 18 30 9 24 18 14 12 13 11 3 10 26 13 11 1 16 13 11 4]

  foreach amsterdam_bus_stops_names [
    create-bus_stops 1 [
      let i position ? amsterdam_bus_stops_names
      set name ?
      set xcor item i xs
      set ycor item i ys
      set size 2
      set shape "gvb-logo"
      set passengers_waiting []
      set passengers_that_arrived 0
      set color 109.9
    ]
  ]
  build-connections
end

to build-connections
  let connections [[15 14 22] [19 23 11] [8] [9 20 4 16] [5 10] [10 17 16] [8] [13 1 17] [9] [20] [17 13 21] [17 16] [20 22 15] [22 23] [23] [18] [] [] [] [23] [21] [22] [] []]
  let i 0
  foreach connections [
    if length ? > 0 [
      foreach ?1 [
        ask bus_stop i [
          create-route-with bus_stop ?1
        ]
      ]
    ]
    set i i + 1
  ]
  update-routes
end

to update-routes
  ask routes [
    let xcors []
    let ycors []
    ask n-of 2 both-ends [
      set xcors lput xcor xcors
      set ycors lput ycor ycors
    ]
    set route_size sqrt (((item 0 xcors - item 1 xcors) ^ 2) + ((item 0 ycors - item 1 ycors) ^ 2))
    hide-link
  ]
end

to-report get-distance [bs1 bs2]
  let return -1
  ifelse is-number? bs1 = false or is-number? bs2 = false [
    show (word "WARNING: get-distance                  : no link between " bs1 " and " bs2)
  ]
  [
    if is-link? route bs1 bs2 [
      ask route bs1 bs2 [
        set return route_size
      ]
    ]
  ]
  if return = -1 [ show (word "WARNING: get-distance                  : no link between " bs1 " and " bs2)]
  report return
end

to go
  let got_a_tick_error false
  ifelse days = 2
  [
    stop
  ]
  [
    carefully
    [
      tick
    ]
    [
      set got_a_tick_error true
      user-message "You must click on setup first. In case you pressed the go button in 'forever' mode, please press 'Halt'."
    ]
    if not got_a_tick_error [
      set-time
      update-passengers-statistics
      update-bus-stops
      ask buses [
        execute-actions
      ]
      add-buses
    ]
  ]
end

to set-time
  ifelse ticks = 0
  [
    set days 1
    set hours 0
    set minutes 0
  ]
  [
    set minutes minutes + 1
    if minutes > 59 [
      set minutes 0
      set hours hours + 1
      if hours > 23 [
        set hours 0
        set days days + 1
        if days < 2 [
          get-daily-ridership-schedule
        ]
      ]
    ]
  ]
  let hours_string (word hours)
  let minutes_string (word minutes)
  if minutes < 10 [
    set minutes_string (word "0" minutes)
  ]
  if hours < 10 [
    set hours_string (word "0" hours)
  ]
  set current_time (word hours_string ":" minutes_string)
end

to get-daily-ridership-schedule
  let file_name (word "passengers-location_day" days ".csv")
  let daily_ridership_schedule parse-file-information file_name
  foreach daily_ridership_schedule [
    let from_bus_stop item 0 ?
    let to_bus_stop item 1 ?
    let count_passengers item 2 ?
    let check_in_time item 3 ?
    create-passengers count_passengers check_in_time from_bus_stop to_bus_stop
  ]
end

to-report parse-file-information [file_name]
  ;This parser takes into account a given file which contains the format below repeated 24 times.
  ; ;;"DESTINATION";;;;;;;;;;;;;;;;;;;;;;;;
  ; "TIME";"FROM";"Amstel";"Amstelveenseweg"; ..; "Zuid"
  ; "00:00";"Amstel";<value1>;<value2>; ...;<value24>
  ; "00:15";"Amstel";<value1>;<value2>; ...;<value24>
  ; ...
  ; "23:45";"Amstel";<value1>;<value2>; ...;<value24>
  ; "00:00";"Amstelveenseweg";<value1>;<value2>; ...;<value24>
  ; ...
  ; "23:45";"Zuid";<value1>;<value2>; ...;<value24>
  let numbers_string ["0" "1" "2" "3" "4" "5" "6" "7" "8" "9"]
  let information []
  file-open file_name
  while [not file-at-end?]
  [
    let line file-read-line
    let ndigits_hour 1
    if item 2 line = ":" [set ndigits_hour 2]
    if (item 0 line = "0") or (item 0 line = "1") or (item 0 line = "2") or (item 0 line = "3") or (item 0 line = "4") or (item 0 line = "5") or (item 0 line = "6") or (item 0 line = "7") or (item 0 line = "8") or (item 0 line = "9") [
      let check_in_time substring line 0 (4 + ndigits_hour)
      set line remove check_in_time line
      let separator ";"
      set check_in_time remove separator check_in_time
      if ndigits_hour = 1 [set check_in_time (word "0" check_in_time)]
      while [member? separator line]
      [
        let pos_separator position separator line
        set line replace-item pos_separator line " "
      ]
      set separator " "
      let from_bus_stop ""
      let got_bus_stop_name false
      let char_index 0
      let line_substring ""
      while [not got_bus_stop_name]
      [
        set line_substring substring line char_index (char_index + 1)
        ifelse member? line_substring numbers_string
        [
          set got_bus_stop_name true
        ]
        [
          set from_bus_stop (word from_bus_stop line_substring)
          set char_index (char_index + 1)
        ]
      ]
      set line remove from_bus_stop line
      set from_bus_stop remove separator from_bus_stop
      let from_bus_stop_index position from_bus_stop amsterdam_bus_stops_names
      set line (word "[" line "]")
      let current_schedule_list read-from-string line
      let i 0
      foreach current_schedule_list [
        if ? != 0 [
          let to_bus_stop i
          let current_schedule_information (list from_bus_stop_index to_bus_stop ? check_in_time)
          set information lput current_schedule_information information
        ]
        set i (i + 1)
      ]

    ]
  ]
  file-close
  report information
end

to update-bus-stops
  let pos 0

  foreach passengers [
    let scheduled_time (word item  1 ?)
    if (scheduled_time = current_time) and (item 8 ? = -1) and (item 7 ? = -1) [
      let from_bus_stop item 2 ?
      set ? replace-item 8 ? from_bus_stop
      set passengers replace-item pos passengers ?
      ask bus_stop from_bus_stop [
        let d item 3 ?
        let i item 0 ?
        let p (list i d)
        let posi position p passengers_waiting
        if (is-boolean? posi) and (not posi)[
          set passengers_waiting lput p passengers_waiting
        ]
      ]
    ]
    set pos pos + 1
  ]
  update-bus-stops-colors
end

to create-passengers [count_passengers check_in_time from_bus_stop to_bus_stop]
  if from_bus_stop = to_bus_stop [stop]
  if not is-list? passengers [
    set passengers []
  ]
  let id length passengers
  let cit check_in_time
  let fbs from_bus_stop
  let tbs to_bus_stop
  repeat count_passengers [
    let new_passenger (list id cit fbs tbs 0 0 false -1 -1)
    set passengers lput new_passenger passengers
    set id length passengers
  ]
end

to update-bus-stops-colors
  ask bus_stops [
    ifelse length passengers_waiting <= 10
    [
      set color 109.9
    ]
    [
      ifelse length passengers_waiting > 10 and length passengers_waiting <= 20
      [
        set color 109
      ]
      [
        ifelse length passengers_waiting > 20 and length passengers_waiting <= 30
        [
          set color 108
        ]
        [
          ifelse length passengers_waiting > 30 and length passengers_waiting <= 40
          [
            set color 107
          ]
          [
            ifelse length passengers_waiting > 40 and length passengers_waiting <= 50
            [
              set color 106
            ]
            [
              ifelse length passengers_waiting > 50 and length passengers_waiting <= 60
              [
                set color 105
              ]
              [
                ifelse length passengers_waiting > 60 and length passengers_waiting <= 70
                [
                  set color 104
                ]
                [
                  ifelse length passengers_waiting > 70 and length passengers_waiting <= 80
                  [
                    set color 103
                  ]
                  [
                    ifelse length passengers_waiting > 80 and length passengers_waiting <= 90
                    [
                      set color 102
                    ]
                    [
                      ifelse length passengers_waiting > 90 and length passengers_waiting <= 100
                      [
                        set color 101
                      ]
                      [
                        set color 100
                      ]
                    ]
                  ]
                ]
              ]
            ]
          ]
        ]
      ]
    ]
  ]
end

to add-bus [b_t]
  ifelse is-number? b_t = false or  b_t < 1 or b_t > 3 [
    show (word "WARNING: add-bus                       :" "type of bus does not exist: " b_t)
  ]
  [
    if not is-list? leasing_list [
      set leasing_list []
    ]
    set leasing_list lput b_t leasing_list
  ]
end

to add-buses
  if is-number? leasing_list = true [stop]

  foreach leasing_list [
    let bt ?
    create-buses 1 [
      let cost 0
      set bus_type bt
      ifelse bus_type = 1
      [
        set cost bus_type1_price
        set color green
      ]
      [
        ifelse bus_type = 2
        [
          set cost bus_type2_price
          set color yellow
        ]
        [
          set cost bus_type3_price
          set color red
        ]
      ]
      set inbox []
      update-expenses cost
      set shape "bus"
      set size 2
      set xcor 22
      set ycor 21
      set bus_passengers []
      set bus_id who
      set next_stop -1
      set current_stop 3
      set previous_stop -1
      init-buses
    ]
  ]
  set leasing_list []
end

to-report get-bus-stop-here [x y]
  let b_s_id false
  ask bus_stops [
    if (pxcor = x) and (pycor = y) [
      set b_s_id (position name amsterdam_bus_stops_names)
    ]
  ]
  report b_s_id
end

to-report bus-reached-bus-stop [b_id b_s_id]
  let reached? false
  ask buses [
    let bsh get-bus-stop-here round xcor round ycor
    if (bus_id = b_id) and (not is-boolean? bsh) and (bsh = b_s_id) [
      set reached? true
    ]
  ]
  report reached?
end

to update-expenses [new_outcome]
  set expenses (expenses + new_outcome)
end

to send-message [to_bus_id message]
  ifelse is-number? to_bus_id = false or count buses with [bus_id = to_bus_id] <= 0 [
    show (word "WARNING: send-message                  :" "bus does not exist: " to_bus_id)
  ]
  [
    ask buses with [bus_id = to_bus_id] [
      let sender 0
      ask myself [
        set sender bus_id
      ]
      let content (list ticks sender message)
      set inbox lput content inbox
      set number_of_messages (number_of_messages + 1)
    ]
  ]
end

to travel-to [bs_id]
  if is-number? bs_id = false [
    show (word "WARNING: travel-to                     :" "bus-stop does not exist: " bs_id)
    stop
  ]

  ask buses [
    if self = myself [
      set next_stop bs_id
    ]
  ]
  let next_stop_id int bs_id
  ifelse (next_stop_id > -1) and (next_stop_id < length amsterdam_bus_stops_names)
  [
    let nsx 0
    let nsy 0
    ask bus_stop next_stop_id [
      set nsx xcor
      set nsy ycor
    ]
    ask buses [
      if self = myself [
        ifelse is-adjacent? bus_id next_stop_id
        [
          facexy nsx nsy
          let bsh get-bus-stop-here round xcor round ycor
          if (not is-boolean? bsh) and bsh = current_stop [
            set previous_stop current_stop
          ]
          fd 1
          let cost 0
          ifelse bus_type = 1
          [
            set cost bus_type1_cost_per_patch
          ]
          [
            ifelse bus_type = 2
            [
              set cost bus_type2_cost_per_patch
            ]
            [
              set cost bus_type3_cost_per_patch
            ]
          ]
          update-expenses cost
          set bsh get-bus-stop-here round xcor round ycor
          ifelse (not is-boolean? bsh) and bsh = next_stop
          [
            set current_stop next_stop
            set next_stop -1
          ]
          [
              set current_stop -1
          ]
        ]
        [
          show (word "WARNING: travel-to                     :" "bus-stop is not adjacent: " bs_id)
        ]
      ]
    ]
  ]
  [
    show (word "WARNING: travel-to                     :" "bus-stop does not exist: " bs_id)
  ]
end

to-report is-adjacent? [b_id b_s_id]
  let return false
  ask buses with [bus_id = b_id] [
    let bsh get-bus-stop-here round xcor round ycor
    ifelse (is-boolean? bsh) and (not bsh)
    [
      if (not is-boolean? get-distance previous_stop next_stop) and (b_s_id = next_stop) [
        set return true
      ]
    ]
    [
      if (get-distance b_s_id bsh) != -1[
        set return true
      ]
    ]
  ]
  report return
end

to pick-up-passenger [passenger_id]
  ifelse is-number? passenger_id = false or passenger_id < 0 or passenger_id > length passengers - 1
  [
    show (word "WARNING: pick-up-passenger             :" "passenger does not exist in the system: " passenger_id)
  ]
  [
    let passenger item passenger_id passengers
    let pbs []
    set pbs fput item 0 passenger pbs
    set pbs lput item 3 passenger pbs

    let passenger_bus_stop item 8 passenger
    let passenger_arrived? item 6 passenger
    let passenger_destination item 3 passenger

    if passenger_bus_stop >= 0 [
      ask bus_stop passenger_bus_stop [
        let b_id 0
        let c 0
        let l 0
        let pos1 0
        ask myself [
          set b_id bus_id
          if bus_type = 1 [set c bus_type1_capacity]
          if bus_type = 2 [set c bus_type2_capacity]
          if bus_type = 3 [set c bus_type3_capacity]
          set l (length bus_passengers)
          set pos1 position pbs bus_passengers
        ]
        let pos position pbs passengers_waiting
        ifelse (bus-reached-bus-stop b_id passenger_bus_stop) and (l < c) and (not is-boolean? pos) and (is-boolean? pos1) and (not pos1) and (not passenger_arrived?) and (passenger_destination != passenger_bus_stop) [
          set passenger replace-item 8 passenger -1
          set passenger replace-item 7 passenger b_id
          set passengers replace-item passenger_id passengers passenger
          set passengers_waiting remove-item pos passengers_waiting
          let new_bus_passenger []
          set new_bus_passenger fput passenger_id new_bus_passenger
          set new_bus_passenger lput passenger_destination new_bus_passenger
          ask myself [
            set bus_passengers lput new_bus_passenger bus_passengers
          ]
        ]
        [
          show (word "WARNING: pick-up-passenger             :" "It is impossible to pick up such a passenger:" passenger_id)
        ]
      ]
    ]
  ]
end

to drop-off-passenger [p_id]
  ifelse is-number? p_id = false or p_id < 0 or p_id > length passengers - 1
  [
    show (word "WARNING: drop-off-passenger            :" "passenger does not exist in the system: " p_id)
  ]
  [
    let passenger item p_id passengers
    let pos_passenger p_id

    let bs_id 0
    let b_id 0
    let bps []
    ask buses [
      ask myself [
        set bs_id current_stop
        set bps bus_passengers
        set b_id bus_id
        stop
      ]
    ]
    ask bus_stop bs_id [
      let p filter [item 0 ? = p_id] bps
      let p2 filter [item 0 ? = p_id] passengers_waiting
      ifelse length p > 0 and (item 8 passenger = -1) and (item 7 passenger != -1) and (item 7 passenger = b_id) and (length p2 = 0)
      [
        set p item 0 p
        let pos position p bps
        ask myself [
          set bus_passengers remove-item pos bus_passengers
        ]
        ifelse item 3 passenger = bs_id
        [
          set passenger replace-item 8 passenger -1
          set passenger replace-item 6 passenger true

        ]
        [
          set passengers_waiting lput p passengers_waiting
          set passenger replace-item 8 passenger bs_id
        ]
        set passenger replace-item 7 passenger -1
        set passengers replace-item pos_passenger passengers passenger
      ]
      [
        show (word "WARNING: drop-off-passenger            :" "It is impossible to drop off such a passenger: " p_id)
      ]
    ]
  ]
end

to-report get-passengers-at-stop [b_s_id]
  let information []
  ifelse is-number? b_s_id = false or count bus_stops with [who = b_s_id] <= 0 [
     show (word "WARNING: get-passengers-waiting-at-stop:" " there is not bus-stop " b_s_id)]
  [
    ask bus_stop b_s_id [
      foreach passengers_waiting [
        let i item 0 ?
        let p item i passengers
        if item 6 p = false [
          set information lput ? information
        ]
      ]
    ]
  ]

  report information
end
@#$#@#$#@
GRAPHICS-WINDOW
21
12
1097
849
-1
-1
26.0
1
10
1
1
1
0
0
0
1
0
40
0
30
0
0
1
ticks
30.0

BUTTON
1096
12
1162
45
NIL
setup
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

MONITOR
1097
108
1162
153
DAYS
days
17
1
11

BUTTON
1096
44
1162
77
NIL
go
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
1096
76
1162
109
NIL
go
T
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

MONITOR
1097
151
1162
196
TIME
current_time
17
1
11

MONITOR
1097
238
1336
283
Buses' Expenses
expenses
2
1
11

MONITOR
1097
194
1336
239
Passengers' Average Travelling Time
average_travelling_time
2
1
11

MONITOR
1097
504
1336
549
Number of Passengers Waiting for a Bus
amount_passengers_waiting
2
1
11

MONITOR
1097
282
1336
327
Number of Messages Sent by the Buses
number_of_messages
2
1
11

PLOT
21
848
335
1066
Average Travelling Time
Ticks
Average Travelling Time
0.0
10.0
0.0
10.0
true
false
"" ""
PENS
"default" 1.0 0 -16777216 true "" "plot average_travelling_time"
"pen-1" 1.0 0 -7500403 true "" ""

PLOT
335
848
649
1066
Buses Expenses
Ticks
Expenses
0.0
10.0
0.0
10.0
true
false
"" ""
PENS
"default" 1.0 0 -16777216 true "" "plot expenses"

PLOT
648
848
962
1066
Messages Sent by the Buses
Ticks
Number of Messages
0.0
10.0
0.0
10.0
true
false
"" ""
PENS
"default" 1.0 0 -16777216 true "" "plot number_of_messages"

PLOT
1096
327
1336
477
Number of Passengers Waiting for a Bus
NIL
NIL
0.0
10.0
0.0
10.0
true
false
"" ""
PENS
"default" 1.0 0 -16777216 true "" "plot amount_passengers_waiting"

MONITOR
1097
549
1336
594
NIL
average_travelling_time_remaining
17
1
11

MONITOR
1097
627
1340
672
NIL
final_average_travelling_time
17
1
11

@#$#@#$#@
## WHAT IS IT?

(a general understanding of what the model is trying to show or explain)

## HOW IT WORKS

(what rules the agents use to create the overall behavior of the model)

## HOW TO USE IT

(how to use the model, including a description of each of the items in the Interface tab)

## THINGS TO NOTICE

(suggested things for the user to notice while running the model)

## THINGS TO TRY

(suggested things for the user to try to do (move sliders, switches, etc.) with the model)

## EXTENDING THE MODEL

(suggested things to add or change in the Code tab to make the model more complicated, detailed, accurate, etc.)

## NETLOGO FEATURES

(interesting or unusual features of NetLogo that the model uses, particularly in the Code tab; or where workarounds were needed for missing features)

## RELATED MODELS

(models in the NetLogo Models Library and elsewhere which are of related interest)

## CREDITS AND REFERENCES

(a reference to the model's URL on the web if it has one, as well as any other necessary credits, citations, and links)
@#$#@#$#@
default
true
0
Polygon -7500403 true true 150 5 40 250 150 205 260 250

airplane
true
0
Polygon -7500403 true true 150 0 135 15 120 60 120 105 15 165 15 195 120 180 135 240 105 270 120 285 150 270 180 285 210 270 165 240 180 180 285 195 285 165 180 105 180 60 165 15

arrow
true
0
Polygon -7500403 true true 150 0 0 150 105 150 105 293 195 293 195 150 300 150

box
false
0
Polygon -7500403 true true 150 285 285 225 285 75 150 135
Polygon -7500403 true true 150 135 15 75 150 15 285 75
Polygon -7500403 true true 15 75 15 225 150 285 150 135
Line -16777216 false 150 285 150 135
Line -16777216 false 150 135 15 75
Line -16777216 false 150 135 285 75

bug
true
0
Circle -7500403 true true 96 182 108
Circle -7500403 true true 110 127 80
Circle -7500403 true true 110 75 80
Line -7500403 true 150 100 80 30
Line -7500403 true 150 100 220 30

bus
false
0
Polygon -7500403 true true 15 206 15 150 15 120 30 105 270 105 285 120 285 135 285 206 270 210 30 210
Rectangle -16777216 true false 36 126 231 159
Line -7500403 false 60 135 60 165
Line -7500403 false 60 120 60 165
Line -7500403 false 90 120 90 165
Line -7500403 false 120 120 120 165
Line -7500403 false 150 120 150 165
Line -7500403 false 180 120 180 165
Line -7500403 false 210 120 210 165
Line -7500403 false 240 135 240 165
Rectangle -16777216 true false 15 174 285 182
Circle -16777216 true false 48 187 42
Rectangle -16777216 true false 240 127 276 205
Circle -16777216 true false 195 187 42
Line -7500403 false 257 120 257 207

butterfly
true
0
Polygon -7500403 true true 150 165 209 199 225 225 225 255 195 270 165 255 150 240
Polygon -7500403 true true 150 165 89 198 75 225 75 255 105 270 135 255 150 240
Polygon -7500403 true true 139 148 100 105 55 90 25 90 10 105 10 135 25 180 40 195 85 194 139 163
Polygon -7500403 true true 162 150 200 105 245 90 275 90 290 105 290 135 275 180 260 195 215 195 162 165
Polygon -16777216 true false 150 255 135 225 120 150 135 120 150 105 165 120 180 150 165 225
Circle -16777216 true false 135 90 30
Line -16777216 false 150 105 195 60
Line -16777216 false 150 105 105 60

car
false
0
Polygon -7500403 true true 300 180 279 164 261 144 240 135 226 132 213 106 203 84 185 63 159 50 135 50 75 60 0 150 0 165 0 225 300 225 300 180
Circle -16777216 true false 180 180 90
Circle -16777216 true false 30 180 90
Polygon -16777216 true false 162 80 132 78 134 135 209 135 194 105 189 96 180 89
Circle -7500403 true true 47 195 58
Circle -7500403 true true 195 195 58

circle
false
0
Circle -7500403 true true 0 0 300

circle 2
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240

cow
false
0
Polygon -7500403 true true 200 193 197 249 179 249 177 196 166 187 140 189 93 191 78 179 72 211 49 209 48 181 37 149 25 120 25 89 45 72 103 84 179 75 198 76 252 64 272 81 293 103 285 121 255 121 242 118 224 167
Polygon -7500403 true true 73 210 86 251 62 249 48 208
Polygon -7500403 true true 25 114 16 195 9 204 23 213 25 200 39 123

cylinder
false
0
Circle -7500403 true true 0 0 300

dot
false
0
Circle -7500403 true true 90 90 120

face happy
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 255 90 239 62 213 47 191 67 179 90 203 109 218 150 225 192 218 210 203 227 181 251 194 236 217 212 240

face neutral
false
0
Circle -7500403 true true 8 7 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Rectangle -16777216 true false 60 195 240 225

face sad
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 168 90 184 62 210 47 232 67 244 90 220 109 205 150 198 192 205 210 220 227 242 251 229 236 206 212 183

fish
false
0
Polygon -1 true false 44 131 21 87 15 86 0 120 15 150 0 180 13 214 20 212 45 166
Polygon -1 true false 135 195 119 235 95 218 76 210 46 204 60 165
Polygon -1 true false 75 45 83 77 71 103 86 114 166 78 135 60
Polygon -7500403 true true 30 136 151 77 226 81 280 119 292 146 292 160 287 170 270 195 195 210 151 212 30 166
Circle -16777216 true false 215 106 30

flag
false
0
Rectangle -7500403 true true 60 15 75 300
Polygon -7500403 true true 90 150 270 90 90 30
Line -7500403 true 75 135 90 135
Line -7500403 true 75 45 90 45

flower
false
0
Polygon -10899396 true false 135 120 165 165 180 210 180 240 150 300 165 300 195 240 195 195 165 135
Circle -7500403 true true 85 132 38
Circle -7500403 true true 130 147 38
Circle -7500403 true true 192 85 38
Circle -7500403 true true 85 40 38
Circle -7500403 true true 177 40 38
Circle -7500403 true true 177 132 38
Circle -7500403 true true 70 85 38
Circle -7500403 true true 130 25 38
Circle -7500403 true true 96 51 108
Circle -16777216 true false 113 68 74
Polygon -10899396 true false 189 233 219 188 249 173 279 188 234 218
Polygon -10899396 true false 180 255 150 210 105 210 75 240 135 240

gvb-logo
false
0
Polygon -7500403 true true 165 60 120 105 60 105 60 135 120 135 165 90
Polygon -7500403 true true 135 240 180 195 240 195 240 165 180 165 135 210
Polygon -7500403 true true 240 105 180 105 120 165 60 165 60 195 120 195 180 135 240 135 240 105

house
false
0
Rectangle -7500403 true true 45 120 255 285
Rectangle -16777216 true false 120 210 180 285
Polygon -7500403 true true 15 120 150 15 285 120
Line -16777216 false 30 120 270 120

leaf
false
0
Polygon -7500403 true true 150 210 135 195 120 210 60 210 30 195 60 180 60 165 15 135 30 120 15 105 40 104 45 90 60 90 90 105 105 120 120 120 105 60 120 60 135 30 150 15 165 30 180 60 195 60 180 120 195 120 210 105 240 90 255 90 263 104 285 105 270 120 285 135 240 165 240 180 270 195 240 210 180 210 165 195
Polygon -7500403 true true 135 195 135 240 120 255 105 255 105 285 135 285 165 240 165 195

line
true
0
Line -7500403 true 150 0 150 300

line half
true
0
Line -7500403 true 150 0 150 150

ns-logo
false
0
Polygon -7500403 true true 90 120 150 120 150 135 90 135 90 120
Polygon -7500403 true true 75 150 135 150 135 165 75 165 75 150
Polygon -7500403 true true 150 135 210 135 210 150 150 150 150 135
Polygon -7500403 true true 135 165 195 165 195 180 135 180 135 165
Polygon -13345367 true false 105 240 165 240 120 240
Polygon -7500403 true true 120 165 135 180 150 165 135 150 120 165
Polygon -7500403 true true 135 135 150 150 165 135 150 120
Polygon -7500403 true true 90 120 60 150 90 195 105 195 75 150 90 135
Polygon -7500403 true true 195 180 225 150 195 105 180 105 210 150 195 165

pentagon
false
0
Polygon -7500403 true true 150 15 15 120 60 285 240 285 285 120

person
false
0
Circle -7500403 true true 110 5 80
Polygon -7500403 true true 105 90 120 195 90 285 105 300 135 300 150 225 165 300 195 300 210 285 180 195 195 90
Rectangle -7500403 true true 127 79 172 94
Polygon -7500403 true true 195 90 240 150 225 180 165 105
Polygon -7500403 true true 105 90 60 150 75 180 135 105

plant
false
0
Rectangle -7500403 true true 135 90 165 300
Polygon -7500403 true true 135 255 90 210 45 195 75 255 135 285
Polygon -7500403 true true 165 255 210 210 255 195 225 255 165 285
Polygon -7500403 true true 135 180 90 135 45 120 75 180 135 210
Polygon -7500403 true true 165 180 165 210 225 180 255 120 210 135
Polygon -7500403 true true 135 105 90 60 45 45 75 105 135 135
Polygon -7500403 true true 165 105 165 135 225 105 255 45 210 60
Polygon -7500403 true true 135 90 120 45 150 15 180 45 165 90

sheep
false
15
Circle -1 true true 203 65 88
Circle -1 true true 70 65 162
Circle -1 true true 150 105 120
Polygon -7500403 true false 218 120 240 165 255 165 278 120
Circle -7500403 true false 214 72 67
Rectangle -1 true true 164 223 179 298
Polygon -1 true true 45 285 30 285 30 240 15 195 45 210
Circle -1 true true 3 83 150
Rectangle -1 true true 65 221 80 296
Polygon -1 true true 195 285 210 285 210 240 240 210 195 210
Polygon -7500403 true false 276 85 285 105 302 99 294 83
Polygon -7500403 true false 219 85 210 105 193 99 201 83

square
false
0
Rectangle -7500403 true true 30 30 270 270

square 2
false
0
Rectangle -7500403 true true 30 30 270 270
Rectangle -16777216 true false 60 60 240 240

star
false
0
Polygon -7500403 true true 151 1 185 108 298 108 207 175 242 282 151 216 59 282 94 175 3 108 116 108

target
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240
Circle -7500403 true true 60 60 180
Circle -16777216 true false 90 90 120
Circle -7500403 true true 120 120 60

tree
false
0
Circle -7500403 true true 118 3 94
Rectangle -6459832 true false 120 195 180 300
Circle -7500403 true true 65 21 108
Circle -7500403 true true 116 41 127
Circle -7500403 true true 45 90 120
Circle -7500403 true true 104 74 152

triangle
false
0
Polygon -7500403 true true 150 30 15 255 285 255

triangle 2
false
0
Polygon -7500403 true true 150 30 15 255 285 255
Polygon -16777216 true false 151 99 225 223 75 224

truck
false
0
Rectangle -7500403 true true 4 45 195 187
Polygon -7500403 true true 296 193 296 150 259 134 244 104 208 104 207 194
Rectangle -1 true false 195 60 195 105
Polygon -16777216 true false 238 112 252 141 219 141 218 112
Circle -16777216 true false 234 174 42
Rectangle -7500403 true true 181 185 214 194
Circle -16777216 true false 144 174 42
Circle -16777216 true false 24 174 42
Circle -7500403 false true 24 174 42
Circle -7500403 false true 144 174 42
Circle -7500403 false true 234 174 42

turtle
true
0
Polygon -10899396 true false 215 204 240 233 246 254 228 266 215 252 193 210
Polygon -10899396 true false 195 90 225 75 245 75 260 89 269 108 261 124 240 105 225 105 210 105
Polygon -10899396 true false 105 90 75 75 55 75 40 89 31 108 39 124 60 105 75 105 90 105
Polygon -10899396 true false 132 85 134 64 107 51 108 17 150 2 192 18 192 52 169 65 172 87
Polygon -10899396 true false 85 204 60 233 54 254 72 266 85 252 107 210
Polygon -7500403 true true 119 75 179 75 209 101 224 135 220 225 175 261 128 261 81 224 74 135 88 99

wheel
false
0
Circle -7500403 true true 3 3 294
Circle -16777216 true false 30 30 240
Line -7500403 true 150 285 150 15
Line -7500403 true 15 150 285 150
Circle -7500403 true true 120 120 60
Line -7500403 true 216 40 79 269
Line -7500403 true 40 84 269 221
Line -7500403 true 40 216 269 79
Line -7500403 true 84 40 221 269

wolf
false
0
Polygon -16777216 true false 253 133 245 131 245 133
Polygon -7500403 true true 2 194 13 197 30 191 38 193 38 205 20 226 20 257 27 265 38 266 40 260 31 253 31 230 60 206 68 198 75 209 66 228 65 243 82 261 84 268 100 267 103 261 77 239 79 231 100 207 98 196 119 201 143 202 160 195 166 210 172 213 173 238 167 251 160 248 154 265 169 264 178 247 186 240 198 260 200 271 217 271 219 262 207 258 195 230 192 198 210 184 227 164 242 144 259 145 284 151 277 141 293 140 299 134 297 127 273 119 270 105
Polygon -7500403 true true -1 195 14 180 36 166 40 153 53 140 82 131 134 133 159 126 188 115 227 108 236 102 238 98 268 86 269 92 281 87 269 103 269 113

x
false
0
Polygon -7500403 true true 270 75 225 30 30 225 75 270
Polygon -7500403 true true 30 75 75 30 270 225 225 270

@#$#@#$#@
NetLogo 5.3.1
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
default
0.0
-0.2 0 0.0 1.0
0.0 1 1.0 0.0
0.2 0 0.0 1.0
link direction
true
0

@#$#@#$#@
0
@#$#@#$#@
