import os

import sample_generation

directory_path = "E:/year3_sem1/SA/video_image/1-50-transcript/handle"

video_lst = os.listdir(directory_path)
for video in video_lst:
    subdir_path = os.path.join(directory_path, video)
    if os.path.isdir(subdir_path):
        file_path = os.path.join(subdir_path, 'capspeaker.txt')

        with open(file_path, 'r') as file:
            conversation = file.readlines()

            for i in range(len(conversation)):
                conversation[i] = f"{i+1}. {conversation[i]}"
            # interviewee_path_dic, interviewer_path_dic = sample_generation.findSpeakers(directory_path)
            # interviewee = interviewee_path_dic[video]
            # interviewer = interviewer_path_dic[video]



        with open(f"{subdir_path}/capspeaker1.txt", 'w') as file:
            file.writelines(conversation)



