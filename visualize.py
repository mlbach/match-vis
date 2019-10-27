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


def draw_clock(img, elapsed_time, position=(50, 50)):

    tlx = position[0] # top left position, x-axis
    tly = position[1] # top left position y-axis
    

    cv2.rectangle(img, (tlx, tly), (tlx + 100, tly + 40), (250,250,250), -1) #filled white box
    cv2.rectangle(img, (tlx, tly), (tlx + 100, tly + 40), (0, 0, 0)) #black border
    
    cv2.putText(img, elapsed_time, 
                (tlx + 5, tly + 33), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)
                

def visualize(blank_image, ts, filename, save_video, vid_fps, player_focus):
    
    if opt.player_focus != None:
        focus_image = np.zeros((40 * 10 + 25, 20 * 10 + 25, 3), np.uint8) #construct second image for player focus, dimensions rotated
        focus_image[:, :, 1] = 204
        
        cv2.putText(focus_image, "Focus on player "+player_focus, (10, 10), cv2.FONT_HERSHEY_PLAIN, 1, (0,0,0), 1)
        
        cv2.rectangle(focus_image, (12, 12), 
        (focus_image.shape[1] - 13, focus_image.shape[0] - 13), (250,250,250))
        
    if save_video:
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
        
        vid_writer = cv2.VideoWriter(vid_path, cv2.VideoWriter_fourcc(*'XVID'), vid_fps, (width, height)) #avc1
        
        print("Saving the match visualization to video.")
    
    starttime = datetime.strptime(ts[0][1], '%d %B %Y %H:%M:%S.%f')
    
    for x in range(0, len(ts)):
        base_img = blank_image.copy()
        now = datetime.strptime(ts[x][1], '%d %B %Y %H:%M:%S.%f')
    
        draw_clock(base_img, get_elapsed_time(starttime, now), (int(round(w/2, 0)) - 50,25))
        
        for obj in range(2, len(ts[x])):
            
            x_t = int(round(ts[x][obj][2] * scf)) + border_top
            y_t = int(round(ts[x][obj][3] * scf)) + border_left
            
            if ts[x][obj][1][0] == "A":
                type = "player"
            else:
                type = "ball"
            number = ts[x][obj][1][-2:]
            
            if type == "player":
                cv2.circle(base_img, (y_t, x_t),13, (250, 0, 0), -1)
                cv2.putText(base_img, number, (y_t - 10, x_t + 5), cv2.FONT_HERSHEY_PLAIN, 1, (250,250,250), 2)
                
                if ts[x][obj][1] == player_focus:
                    cv2.circle(focus_image, (int(x_t/2), int(y_t/2)), 1, (250, 0, 0), 1)
                
            else:
                cv2.circle(base_img, (y_t, x_t),8, (250, 250, 250), -1) #ball
                
        if save_video:
            vid_writer.write(base_img)
        else:
            cv2.imshow('image', base_img)
            if player_focus != None:
                cv2.imshow('focus', focus_image)
            if x == len(ts)-1:
                cv2.waitKey(0)
            else:
                cv2.waitKey(1)
                
    if save_video:
        vid_writer.release()

def get_elapsed_time(starttime, now):
    
    duration_in_s = (now - starttime).total_seconds()                        
    minutes = divmod(duration_in_s, 60)           # Use remainder of hours to calc minutes
    seconds = divmod(minutes[1], 1)               # Use remainder of minutes to calc seconds
    return "%02d:%02d" % (minutes[0], seconds[0])
 

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
            #ts = [split_convert_line(next(f).strip()) for x in range(100)] #read only x lines
            for line in f:
                ts.append(split_convert_line(line))

        #print(len(ts))
        print(ts[:5])
        
        realtime_start = datetime.strptime(ts[0][1], '%d %B %Y %H:%M:%S.%f')        # Random date in the past
        realtime_stop  = datetime.strptime(ts[-1][1], '%d %B %Y %H:%M:%S.%f')                         # Now
        realtime_duration = realtime_stop - realtime_start                        # For build-in functions
        rt_duration_in_s = realtime_duration.total_seconds()
        #print(rt_duration_in_s)
        minutes = divmod(rt_duration_in_s, 60)           # Use remainder of hours to calc minutes
        seconds = divmod(minutes[1], 1)               # Use remainder of minutes to calc seconds
        print("Real match duration= %d:%d" % (minutes[0], seconds[0]))
        
        if opt.save_video:
            vid_fps = int(round(len(ts) / rt_duration_in_s, 0)) 
            print("Frame rate", vid_fps)
        else:
            vid_fps = None
        
        
        scf = 10 * 2
        offset_y = 200
        offset_x = 50
        border_top = int(round(offset_y/2, 0))
        border_left = int(round(offset_x/2, 0))

        # bild dimensionen
        h = 20 * scf + offset_y #height
        w = 40 * scf + offset_x #width 40 * 10 * 2

        blank_image = np.zeros((h, w, 3), np.uint8)
        blank_image[:, :, 1 ] = 204 #0, 204, 0 #rgb

        #spielfelddimensionen
        cv2.rectangle(blank_image, (border_left, border_top), 
        (w - border_left, h - border_top), (250,250,250))
        
        
        displaytime_start = datetime.now()
        
        visualize(blank_image, ts, file, opt.save_video, vid_fps, opt.player_focus) #display animation
        
        displaytime_stop = datetime.now()
        displaytime_duration = displaytime_stop - displaytime_start
        dt_duration_in_s = displaytime_duration.total_seconds()
        minutes = divmod(dt_duration_in_s, 60)
        seconds = divmod(minutes[1], 1)
        print("Display match duration= %d:%d" % (minutes[0], seconds[0]))