


export interface Video {
    key:string;
    favorite:boolean;
    captureTime:Date;
}


export class Server extends EventTarget {
    public static VIDEOS_CHANGED_EVENT = "videosChanged"
    public videos:Array<Video> = []
    public loaded:boolean = false;

    constructor(public apiRoot:string) {
        super()
    }

    private notifyVideos() {
        this.dispatchEvent(new Event(Server.VIDEOS_CHANGED_EVENT))
    }
    async load() {
        if(this.loaded === true)
            return;
        this.loaded = true;
                    
        let videoData = await (await fetch(this.apiRoot + "dance")).json()
        this.videos = videoData;
        console.log(`videos are ${this.videos}`)
        this.notifyVideos();
    }
}