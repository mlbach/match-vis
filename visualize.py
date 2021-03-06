import re
import time
from datetime import datetime
import cv2
import numpy as np
from random import randint
import argparse
import pathlib


def split_convert_line(line_str):
    timestamp = int(line_str.split(',')[0]) #gets timestamp
    line = [timestamp , datetime.fromtimestamp((timestamp/1000)).strftime('%d %B %Y %H:%M:%S.%f')] #convert timestamp to datetime str
    re_groups = re.findall(r'\[([^\[\]]+)\]', line_str) #split str on sublist/player level
    lst = []
    for player in re_groups:
        plo = player.split(',')
        lst.append(list(plo[:2]) + list(map(float, plo[2:]))) #converst numbers from str to float
    return line + lst


def draw_clock(img, visual_params, elapsed_time, position=(50, 50)):

    tlx = position[0] # top left position, x-axis
    tly = position[1] # top left position y-axis
    

    cv2.rectangle(img, (tlx, tly), (tlx + 100, tly + 40), (250,250,250), -1) #filled white box
    cv2.rectangle(img, (tlx, tly), (tlx + 100, tly + 40), (0, 0, 0)) #black border
    
    cv2.putText(img, elapsed_time, 
                (tlx + 5, tly + 33), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)
                
def draw_clock_scoreboard(img, score, visual_params, elapsed_time, position=(50, 50)):

    tlx = position[0] # top left position, x-axis
    tly = position[1] # top left position y-axis

    scoreboard_width = 60
    
    tlx_this = tlx
    tlx_next = tlx_this + 20
    cv2.rectangle(img, (tlx_this, tly), (tlx_next, tly + 40), (250,0,0), -1) #filled blue box
    cv2.rectangle(img, (tlx_this, tly), (tlx_next, tly + 40), (0, 0, 0)) #black border
    
    tlx_this = tlx_next
    tlx_next = tlx_this + 140
    cv2.rectangle(img, (tlx_this, tly), (tlx_next, tly + 40), (211,211,211), -1) #filled white box
    cv2.rectangle(img, (tlx_this, tly), (tlx_next, tly + 40), (0, 0, 0)) #black border
    cv2.putText(img, "Team L", 
                (tlx_this + 5, tly + 33), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)
    
    tlx_this = tlx_next
    tlx_next = tlx_this + 60
    cv2.rectangle(img, (tlx_this, tly), (tlx_next, tly + 40), (250,250,250), -1) #filled white box
    cv2.rectangle(img, (tlx_this, tly), (tlx_next, tly + 40), (0, 0, 0)) #black border
    
    cv2.putText(img, str(score[0])+":"+str(score[1]), 
                (tlx_this + 5, tly + 33), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)
    
    tlx_this = tlx_next
    tlx_next = tlx_this + 140
    cv2.rectangle(img, (tlx_this, tly), (tlx_next, tly + 40), (211,211,211), -1) #filled white box
    cv2.rectangle(img, (tlx_this, tly), (tlx_next, tly + 40), (0, 0, 0)) #black border
    
    cv2.putText(img, "Team R", 
                (tlx_this + 5, tly + 33), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)
                
    tlx_this = tlx_next
    tlx_next = tlx_this + 20
    cv2.rectangle(img, (tlx_this, tly), (tlx_next, tly + 40), (250,0,0), -1) #filled blue box
    cv2.rectangle(img, (tlx_this, tly), (tlx_next, tly + 40), (0, 0, 0)) #black border
    
    
    tlx_this = tlx_next
    tlx_next = tlx_this + 100            

    cv2.rectangle(img, (tlx_this, tly), (tlx_next, tly + 40), (79,79,47), -1) #filled white box
    cv2.rectangle(img, (tlx_this, tly), (tlx_next, tly + 40), (0, 0, 0)) #black border
    
    cv2.putText(img, elapsed_time, 
                (tlx_this + 5, tly + 33), cv2.FONT_HERSHEY_SIMPLEX, 1, (250,250,250), 2)

def visualize(blank_image, ts, filename, visual_params, player_focus):
    padding_x = visual_params["offset_x"] * visual_params["magnitude"]
    padding_y = visual_params["offset_y"] * visual_params["magnitude"]
    
    border_top = int(round(padding_y/2, 0))
    border_left = int(round(padding_x/2, 0))
    
    h = 20 * visual_params["magnitude"] * visual_params["scf"] + padding_y #height
    w = 40 * visual_params["magnitude"] * visual_params["scf"] + padding_x #width 40 * 10 * 2
    
    in_goal = False
    score = np.array([0, 0], np.uint8)
    
    if opt.player_focus != None:
        focus_pitch = construct_focus_pitch(player_focus, visual_params)
        
    if visual_params["save_video"]:
        vid_path, vid_writer = None, None
        
        
        if filename.find("/") > -1:
            filename = filename.split("/")[-1] #without folders
            
        print(filename)
        vid_path = 'videos/'+filename[:-3]+'avi' #avi
        print(vid_path)
        '''if isinstance(vid_writer, cv2.VideoWriter):
            vid_writer.release()  # release previous video writer
        '''
        width = blank_image.shape[1]
        height = blank_image.shape[0]
        
        vid_writer = cv2.VideoWriter(vid_path, cv2.VideoWriter_fourcc(*'XVID'), visual_params["vid_fps"], (width, height)) #avc1
        
        print("Saving the match visualization to video.")
    
    starttime = datetime.strptime(ts[0][1], '%d %B %Y %H:%M:%S.%f')
    
    for x in range(1500, len(ts)):
        base_img = blank_image.copy()
        now = datetime.strptime(ts[x][1], '%d %B %Y %H:%M:%S.%f')
    
        draw_clock_scoreboard(base_img, score, visual_params, get_elapsed_time(starttime, now), (int(round(w/2, 0)) - 50,25))
        
        for obj in range(2, len(ts[x])):
            
            x_t = int(round(ts[x][obj][2] * visual_params["scf"] * visual_params["magnitude"])) + border_top
            y_t = int(round(ts[x][obj][3] * visual_params["scf"] * visual_params["magnitude"])) + border_left
            
            if ts[x][obj][1][0] == "A":
                type = "player"
            else:
                type = "ball"
            number = ts[x][obj][1][-2:]
            
            if type == "player":
                cv2.circle(base_img, (y_t, x_t),13, (250, 0, 0), -1)
                cv2.putText(base_img, number, (y_t - 10, x_t + 5), cv2.FONT_HERSHEY_PLAIN, 1, (250,250,250), 2)
                
                if ts[x][obj][1] == player_focus:
                    cv2.circle(focus_pitch, 
                            (int(round((ts[x][obj][2] * visual_params["scf"] * visual_params["magnitude"]  + border_left)/2)), #focus pitch uses equal padding
                            int(round((ts[x][obj][3] * visual_params["scf"] * visual_params["magnitude"]  + border_left)/2))),
                            1, (250, 0, 0), 1)
                
            else:
                cv2.circle(base_img, (y_t, x_t),8, (250, 250, 250), -1) #ball
                in_goal, score = check_goal((y_t, x_t), in_goal, score)
                
        if visual_params["save_video"]:
            vid_writer.write(base_img)
        else:
            cv2.imshow('image', base_img)
            if player_focus != None:
                flipped_focus = cv2.flip(focus_pitch.copy(), 0)
                cv2.putText(flipped_focus, "Focus on player "+player_focus, (10, 10), cv2.FONT_HERSHEY_PLAIN, 1, (0,0,0), 1)
                cv2.imshow('focus', flipped_focus)
            if x == len(ts)-1:
                cv2.waitKey(0)
            else:
                cv2.waitKey(1)
                
    if visual_params["save_video"]:
        vid_writer.release()

def get_elapsed_time(starttime, now):
    
    duration_in_s = (now - starttime).total_seconds()                        
    minutes = divmod(duration_in_s, 60)           # Use remainder of hours to calc minutes
    seconds = divmod(minutes[1], 1)               # Use remainder of minutes to calc seconds
    return "%02d:%02d" % (minutes[0], seconds[0])
 
def check_goal(ball_coords, in_goal, score):
    
    if in_goal:
        if goal_coords[0, 2] < ball_coords[0] < goal_coords[1, 0]:
            in_goal = False #ball again in field of play
    else:
        for i in range(2):
            if (goal_coords[i, 0] < ball_coords[0] < goal_coords[i, 2]) and (goal_coords[i, 1] < ball_coords[1] < goal_coords[i, 3]):
                
                in_goal = True
                score[i] += 1        
    
    return in_goal, score

def get_filenames(example_filename):

    if example_filename.find("/") > -1:
        path = example_filename.split("/") #seperate path, filename 
        dir = "/".join(path[:-1])
        file = path[-1]
    else:
        dir = "."
        file = example_filename

    file = file.split("_")
    file = "_".join(file[:2])
    file += "_*.log" # filename_*suffix*.log

    files = pathlib.Path(dir).glob(file) #find all files that match name

    l = []
    for f in files:
        l.append(f.as_posix().__str__())
    return l

def construct_pitch(params):
    padding_x = params["offset_x"] * params["magnitude"]
    padding_y = params["offset_y"] * params["magnitude"]
    
    border_top = int(round(padding_y/2, 0))
    border_left = int(round(padding_x/2, 0))

    # bild dimensionen
    h = int(20 * params["magnitude"] * params["scf"] + padding_y) #height
    w = int(40 * params["magnitude"] * params["scf"] + padding_x) #width 40 * 10 * 2

    blank_image = np.zeros((h, w, 3), np.uint8)
    blank_image[:, :, 1 ] = 204 #0, 204, 0 #rgb

    
    #add 5m x 2m goals
    post_to_corner = border_top + int(round((20 - 5)/2 * params["magnitude"] * params["scf"], 0))
    leftgoal_tlx = int(border_left -  2 * params["magnitude"] * params["scf"])
    post_to_post = post_to_corner + int(round(5 * params["magnitude"] * params["scf"],0))
    
    rightgoal_tlx = w - border_left
    rightgoal_brx = int(w - border_left +  2 * params["magnitude"] * params["scf"])
    
    global goal_coords
    goal_coords = np.array([
        [leftgoal_tlx, post_to_corner, border_left, post_to_post],
        [rightgoal_tlx, post_to_corner, rightgoal_brx, post_to_post]], np.uint16) #left goal, right goal: tly, tlx, bry, brx
    
    cv2.rectangle(blank_image, (leftgoal_tlx, post_to_corner), 
        (border_left, post_to_post), (0, 0, 0)) # left goal
    
    cv2.rectangle(blank_image, (rightgoal_tlx, post_to_corner), 
        (rightgoal_brx, post_to_post), (0, 0, 0)) # right goal

    #pitch border
    cv2.rectangle(blank_image, (border_left, border_top), 
    (w - border_left, h - border_top), (250,250,250))    
    
    return blank_image

def construct_focus_pitch(focus, params):
    padding_x = (params["offset_x"]/2) * params["magnitude"] # focus pith only half the size
    padding_y = (params["offset_x"]/2) * params["magnitude"] #use equal padding
    
    border_top = int(round(padding_y/2, 0))
    border_left = int(round(padding_x/2, 0))    

    w = int(round(20 * params["magnitude"] * (params["scf"]/2) + padding_y, 0)) # dimensions switched from regular pitch
    h = int(round(40 * params["magnitude"] * (params["scf"]/2) + padding_x, 0)) 
    
    focus_image = np.zeros((h, w, 3), np.uint8) #construct second image for player focus, dimensions rotated
    focus_image[:, :, 1] = 204
    
    cv2.rectangle(focus_image, (border_top, border_top), 
    (focus_image.shape[1] - border_top, focus_image.shape[0] - border_top), (250,250,250))
    
    return focus_image

def calc_duration(datetime_start, datetime_stop):
    duration = datetime_start - datetime_stop                        # For build-in functions
    duration_in_s = duration.total_seconds()
    minutes = divmod(duration_in_s, 60)           # Use remainder of hours to calc minutes
    seconds = divmod(minutes[1], 1)               # Use remainder of minutes to calc seconds 
    
    return minutes[0], seconds[0]

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--match-logs', type=str, default=None, help='match log file to visualize')
    parser.add_argument('--file-sequence', type=bool, default=False, help='true if you want to sequentially load multiple files of the same base name')
    parser.add_argument('--save-video', type=bool, default=False, help='false to display animation, true to save to video')
    parser.add_argument('--player-focus', type=str, default=None, help='expects None or valid externalID of object. if object ID is given, display second screen and follow movement')
    opt = parser.parse_args()
    print(opt)
    
    if opt.match_logs == None:
        raise ValueError('No filename of match logs was given!')
    fn = opt.match_logs
    fn = fn.replace("\\", "/") #unify directory seperator
    
    if opt.file_sequence:
        files = get_filenames(fn)
    else:
        files = [fn]

    for file in files:
        ts = []
        # read data from file
        with open(file) as f:
            for line in f:
                ts.append(split_convert_line(line))

        
        #calculate actual match duration
        min, sec = calc_duration(datetime.strptime(ts[-1][1], '%d %B %Y %H:%M:%S.%f'), datetime.strptime(ts[0][1], '%d %B %Y %H:%M:%S.%f')) #datetime from first, last timesteps
        print("Real match duration= %d:%d" % (min, sec))
        
        visual_parameters = {
            "pitch_height" : 20,
            "pitch_width" : 40,
            "magnitude" : 10,
            "scf" : 2.5, #scaling factor
            "offset_y" : 20,
            "offset_x" : 15,
            "save_video" : opt.save_video,
            "vid_fps" : None
        }
        if opt.save_video:
            visual_parameters["vid_fps"] = int(round(len(ts) / rt_duration_in_s, 0)) 

        pitch = construct_pitch(visual_parameters)
        
        displaytime_start = datetime.now()
        
        visualize(pitch, ts, file, visual_parameters, opt.player_focus) #display animation
        
        #calculate time it took to display visualization
        min, sec = calc_duration(datetime.now(), displaytime_start)
        print("Display match duration= %d:%d" % (min, sec))
