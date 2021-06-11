


export interface Dance {
    id:string;
    favorite:number;
    videofile:string;
    comments: string;
    reviewed: number;
    song: string;
    time: string;
    __index:number;
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
    async reload() {
        this.loaded = true;
        await this._forceLoad();
    }
    async load() {
        if(this.loaded === true)
            return;
        this.loaded = true;
        await this._forceLoad();
    }

    async _forceLoad() {
                    
        let danceData = await (await fetch(this.apiRoot + "dance?hasVideo=true")).json()
        this.dances = danceData.result == 0? danceData.rows:[];
        this.dances = this.dances.map( (r,i) => {return {...r,__index:i}});        
        console.log(`dances are ${this.dances}`)
        this.notifyDances();
    }
    replaceDance(dance:Dance,newValues:Partial<Dance>):Dance {
        let newDance = {...dance,...newValues};
        this.dances[newDance.__index] = newDance;
        this.notifyDances();
        return newDance;
    }

    setFavorite(dance:Dance,newFavorite:number) {
        if(dance.favorite == newFavorite)
            return;
        fetch(this.apiRoot + `dance/${dance.id}`,{
            method: 'PUT',
            body: JSON.stringify({
                favorite: newFavorite
            })
        })
        return this.replaceDance(dance,{favorite:newFavorite})
    }

    markDanceReviewed(dance:Dance) {
        if(dance.reviewed)
            return;
        fetch(this.apiRoot + `dance/${dance.id}`,{
            method: 'PUT',
            body: JSON.stringify({
                reviewed: 1
            })
        })
        return this.replaceDance(dance,{reviewed:1})
    }
    async deleteRejected() {
        await fetch(this.apiRoot + 'dance/operations/deleteRejected',{
            method:"POST",
            body: "{}"
        });
        this.reload();
    }
}

