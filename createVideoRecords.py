

from uuid import uuid4
from remote_storage import S3Storage
from dance_client import DanceClient
from remote import Remote


remote = Remote()

storage = S3Storage()
client = DanceClient(remote,storage)
client.setConfig({"endpoint":"https://api.twofish.studio"})
storage.setConfig({"bucketName":"disco-videos"})

dances = client.getDances()
#print(dances)
linkedVideos = list(map(lambda d: d['videofile'],dances))

# for aDance in dances:
#     print(aDance['videofile'])
#print(dances)
videos = storage.listObjects("videos/")
videosWithoutDances = []
linkedVideoCount = 0
for aVid in videos:
    key = aVid["Key"]
    if not (key in linkedVideos):
        videosWithoutDances.append(aVid)
    else:
        linkedVideoCount += 1

print(f'found {len(videosWithoutDances)} of {len(videos)} unlinked videos')

for aVid in videosWithoutDances:
    print(f'registering {aVid["Key"]} ({aVid["LastModified"]})')
    newDanceID = str(uuid4())
    song = "audio/disco/freakout.wav"
    time = str(aVid["LastModified"])
    videofile = aVid["Key"]
    comments = "restored"
    fields = {
        "song": song,
        "time": time,
        "videofile": videofile,
        "comments": comments
    }
    #print(f'\tdetails are {fields}')
    client.registerNewDance(newDanceID,fields)