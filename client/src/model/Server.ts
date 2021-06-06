


export interface Dance {
    id:string;
    favorite:number;
    videofile:string;
    comments: string;
    reviewed: number;
    song: string;
    time: string;
}


export class Server extends EventTarget {
    public static DANCES_CHANGED_EVENT = "dancesChanged"
    public dances:Array<Dance> = []
    public loaded:boolean = false;

    constructor(public apiRoot:string) {
        super()
    }

    private notifyDances() {
        this.dispatchEvent(new Event(Server.DANCES_CHANGED_EVENT))
    }
    async load() {
        if(this.loaded === true)
            return;
        this.loaded = true;
                    
        let danceData = await (await fetch(this.apiRoot + "dance")).json()
        this.dances = danceData.result == 0? danceData.rows:[];
        console.log(`dances are ${this.dances}`)
        this.notifyDances();
    }
}