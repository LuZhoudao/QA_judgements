import openai
import os
import nltk
import time
import re
import pandas as pd
from check import check_directories


# nltk.download('punkt')


def find_QA(conversation, messages):
    message = conversation
    messages.append({"role": "user", "content": message})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k-0613",
        messages=messages
    )
    reply = response["choices"][0]["message"]["content"]

    return reply

    # print(reply)


def split_results(result):
    pattern = r"\d+\.\s(.+)"
    answers = re.findall(pattern, result)
    for i in range(len(answers)):
        answer = answers[i]
        if answer[-1] == '.':
            answers[i] = answers[i][:-1]
    return answers


def split(conversation, result, interviewee, interviewer):
    line_lst = conversation.split("\n")
    line_lst = line_lst[:-1]
    print(line_lst)
    return_lst = []
    #print(len(line_lst))
    #print(len(result))
    for i in range(len(line_lst)):
        line = line_lst[i]
        jump = 0
        if line[2] == " ":
            jump = 0
        elif line[3] == " ":
            jump = 1
        else:
            jump = 2
        start_time = line[jump+4:jump+17]
        end_time = line[jump+21:jump+33]
        speaker = line[jump+36:jump+46]
        status = "Not sure"
        if interviewee[0] == speaker:
            status = "interviewee"
        elif interviewer[0] == speaker:
            status = "interviewer"
        text = line[jump+49:]
        limit = len(result)
        if i+1 > limit:
            continue
        QA = result[i]
        if QA == "Statement":
            QA = "Nothing"
        if status == "interviewee" and QA == "Question":
            QA = "Nothing"
        if status == "interviewer" and QA == "Answer":
            QA = "Nothing"
        # word_lst = result.split()
        # QA_lst = []
        # question_lst = []
        # answer_lst = []
        # for i in range(len(word_lst)):
        #     word = word_lst[i]
        #     if word.strip().lower() == "question":
        #         question_lst.append(i)
        #     elif word.strip().lower() == "answer":
        #         answer_lst.append(i)
        #
        # if len (question_lst) != len(answer_lst):
        #     return None
        #
        # for q in range(len(question_lst)):
        #     question_start_time = word_lst[question_lst[q] + 1][1:]
        #     question_last_time = ""
        #     for s in range(question_lst[q] + 1, len(word_lst)):
        #         if word_lst[s][-1] == ":":
        #             question_last_time = word_lst[s][:-2]
        #             question = " ".join(word_lst[s+1:answer_lst[q]])
        #             break
        #
        #     answer_start_time = word_lst[answer_lst[q] + 1][1:]
        #     answer_last_time = ""
        #     for s in range(answer_lst[q] + 1, len(word_lst)):
        #         if word_lst[s][-1] == ":":
        #             answer_last_time = word_lst[s][:-2]
        #             if q != len(question_lst) - 1:
        #                 answer = " ".join(word_lst[s+1:question_lst[q + 1]])
        #             else:
        #
        #                 answer = " ".join(word_lst[s+ 1:])
        #             break

        return_lst.append(
            dict(start_time=start_time, end_time=end_time, speaker=speaker, status=status, text=text, QA=QA, ))

    QA = pd.DataFrame(return_lst)
    print(QA)
    return QA


def count_tokens(text):
    tokens = nltk.word_tokenize(text)
    return len(tokens)


def truncate_text(text, max_tokens):
    token_count = count_tokens(text)
    if token_count <= max_tokens:
        return text

    tokens = nltk.word_tokenize(text)
    truncated_tokens = tokens[:max_tokens]
    truncated_text = ' '.join(truncated_tokens)
    return truncated_text


def findSpeakers(handle_path):
    speaker_path_interviewee_dic = {}
    speaker_path_interviewer_dic = {}
    # handle_path = f"{path}/1-50-transcript/handle"
    video_lst = os.listdir(handle_path)
    for video in video_lst:
        specific_video_path = f"{handle_path}/{video}"
        with open(f"{specific_video_path}/Interviewee_Cap.txt", 'r') as f:
            answer = f.read()
            f.close()
        pattern_interviewee = r"\[(\s?)(SPEAKER_0[0-9])(\s?)\] - Interviewee"
        match_ee = re.search(pattern_interviewee, answer)
        speaker_path_interviewee_dic[video] = []
        if not match_ee:
            speaker_path_interviewee_dic[video].append("Don't know who")
        else:
            interviewee = match_ee.group(2)
            speaker_path_interviewee_dic[video].append(interviewee.strip())
        pattern_interviewer = r"\[(\s?)(SPEAKER_0[0-9])(\s?)\] - Interviewer"
        match_er = re.search(pattern_interviewer, answer)
        speaker_path_interviewer_dic[video] = []
        if not match_er:
            speaker_path_interviewee_dic[video].append("Don't know who")
        else:
            interviewer = match_er.group(2)
            speaker_path_interviewer_dic[video].append(interviewer.strip())
    return speaker_path_interviewee_dic, speaker_path_interviewer_dic


if __name__ == "__main__":
    # Set up OpenAI API credentials and max tokens
    openai.api_key = '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'
    max_tokens = 40000

    # Directory path
    directory_path = "E:/year3_sem1/SA/video_image/1-50-transcript/handle"
    result_path = "E:/year3_sem1/SA/video_image/1-50-transcript/result2"
    file_count = 0

    # find interviewee/ers
    interviewee_path_dic, interviewer_path_dic = findSpeakers(directory_path)

    # # Iterate over subdirectories
    count = len(os.listdir(directory_path))

    for i in range(count):
        subdir = os.listdir(directory_path)[i]
        subdir_path = os.path.join(directory_path, subdir)

        interviewee = interviewee_path_dic[subdir]
        interviewer = interviewer_path_dic[subdir]

        messages = []
        messages.append({"role": "system", "content": "You can help to distinguish questions and answers in text."})

        # speaker 1,speakerii谁是interviewee,停顿多少次，gpt-3.5-turbo-16k-0613
        prompt = f"This is a text message of a Q&A interview with a CEO, {interviewee} is the interviewee, {interviewer} is the interviewer. Each line is a quote from the interviewer/interviewee. For each quote, please judge whether it is a question, answer, or nothing. 'Question' is a question posed by the interviewer to the interviewee, typically asking the CEO's opinion on the company's growth or the market; 'Answer' is the interviewees response based on the interviewer's question, generally a specific opinion on something;'Nothing' is the message unrelated to questions and answers. Each line please returns a value, 'Question', 'Answer' or 'Nothing'. lines of {interviewee} cannot return 'Question', lines of {interviewer} cannot return 'Answer'!  There is an example output: 1. Question, 2. Nothing, 3. Answer, 4. Answer, 5. Answer, 6. Answer. Return as many responses as there are lines. Please do not return to other formats"
        # [00:01:010.67 --> 00:01:013.51] [SPEAKER_02]  Well, I'm glad that you said it's a turnaround because that's
        # exactly how I view it. output: Question: [00:01:007.07 --> 00:01:010.29] [SPEAKER_01]  So what's first on
        # the list in terms of trying to turn this company around for you? Answer: [00:01:010.67 --> 00:01:013.51] [
        # SPEAKER_02]  Well, I'm glad that you said it's a turnaround because that's exactly how I view it. Please do
        # not return to other formats" prompt = f"This is a text message of a Q&A interview with a CEO, {interviewee}
        # is the interviewee, {interviewer} is the interviewer. Each line is a quote from the
        # interviewer/interviewee. For each quote, please judge whether it is a question, answer, or nothing. Each
        # line returns a value. An Example of the return: '1. Question, 2. Question,3. Nothing, 4. Answer. Please do
        # not return to other formats" prompt = f"This is a text message of a Q&A interview with a CEO, {interviewee}
        # is the interviewee, {interviewer} is the interviewer. Each line is a quote from the
        # interviewer/interviewee. For each quote, please judge whether it is a question, answer, or nothing.  Please
        # do not return to other formats" Check if it's a directory
        if os.path.isdir(subdir_path):
            file_path = os.path.join(subdir_path, 'capspeaker1.txt')
            # Read the file contents

            new_csv = []
            with open(file_path, 'r') as file:
                conversation = file.read()
                conversation2 = prompt + str(conversation.split("\n")[:-1])
                truncated_text = truncate_text(conversation2, max_tokens)
                # tokens = nltk.word_tokenize(truncated_text)
                # print(len(tokens))

                result = find_QA(truncated_text, messages)
                handled_result = split_results(result)
                char = split(conversation, handled_result, interviewee, interviewer)
                if char is None:
                    continue
                char.to_csv(f"{result_path}/{subdir}.csv")

        # Check if the maximum rate has been reached
        # if file_count % 3 == 0:
        # # Pause for 1 minute
        #     time.sleep(60)

    #
    #
