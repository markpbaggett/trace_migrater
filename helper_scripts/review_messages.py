# Used to Review Messaging to Look for Files that Should be Published Even if They're Not (a 9999)
import os

messages = []
nine_nine_nine_nines = []
should_be_published = []
should_not_be_published = []
which_file = "dissertations_9999.txt"

with open(f"/home/mark/PycharmProjects/trace_migrater/spring_2020/{which_file}", 'r') as nines:
    for line in nines:
        nine_nine_nine_nines.append(line.split('/')[5].replace('.pdf', '').replace('\n', ''))


for path, directories, files in os.walk("/home/mark/PycharmProjects/trace_migrater/spring_2020/MESSAGES/"):
    for file in files:
        with open(f'{path}/{file}') as current_message:
            messages.append(
                (
                    file.replace('_', ":").replace('.plain', ''), current_message.read()
                )
            )

i = 0
j = 0
for message in messages:
    if message[0] in nine_nine_nine_nines:
        if "I have accepted your" in message[1]:
            i += 1
            should_be_published.append(message[0])
        else:
            should_not_be_published.append(message[0])
            j += 1

# print(f"i: {i} and j: {j}")
s = 1
for etd in should_be_published:
    print(f'{s}. {etd}')
    s += 1

