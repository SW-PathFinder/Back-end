import {
    LocalVideoTrack,
    RemoteParticipant,
    RemoteTrack,
    RemoteTrackPublication,
    Room,
    RoomEvent
} from "livekit-client";
import "./App.css";
import { useState } from "react";
import VideoComponent from "./components/VideoComponent";
import AudioComponent from "./components/AudioComponent";

type TrackInfo = {
    trackPublication: RemoteTrackPublication;
    participantIdentity: string;
};

// When running OpenVidu locally, leave these variables empty
// For other deployment type, configure them with correct URLs depending on your deployment
let APPLICATION_SERVER_URL = "";
let LIVEKIT_URL = "";
configureUrls();

function configureUrls() {
    // If APPLICATION_SERVER_URL is not configured, use default value from OpenVidu Local deployment
    if (!APPLICATION_SERVER_URL) {
        if (window.location.hostname === "localhost") {
            APPLICATION_SERVER_URL = "http://localhost:6080/";
        } else {
            APPLICATION_SERVER_URL = "https://" + window.location.hostname + ":6443/";
        }
    }

    // If LIVEKIT_URL is not configured, use default value from OpenVidu Local deployment
    if (!LIVEKIT_URL) {
        if (window.location.hostname === "localhost") {
            LIVEKIT_URL = "ws://182.209.156.41:7880/";
        } else {
            LIVEKIT_URL = "wss://" + "182.209.156.41" + ":7443/";
        }
        LIVEKIT_URL = "ws://182.209.156.41:7880/";
        // LIVEKIT_URL = "wss://13.125.231.212:4443/"
        // LIVEKIT_URL = "ws://localhost:7880/";
    }
}

function App() {
    const [room, setRoom] = useState<Room | undefined>(undefined);
    const [localTrack, setLocalTrack] = useState<LocalVideoTrack | undefined>(undefined);
    const [remoteTracks, setRemoteTracks] = useState<TrackInfo[]>([]);

    const [participantName, setParticipantName] = useState("participant_name");
    const [roomName, setRoomName] = useState("room_name");

    async function joinRoom() {
        // Initialize a new Room object
        const room = new Room();
        setRoom(room);

        // Specify the actions when events take place in the room
        // On every new Track received...
        room.on(
            RoomEvent.TrackSubscribed,
            (_track: RemoteTrack, publication: RemoteTrackPublication, participant: RemoteParticipant) => {
                setRemoteTracks((prev) => [
                    ...prev,
                    { trackPublication: publication, participantIdentity: participant.identity }
                ]);
            }
        );

        // On every Track destroyed...
        room.on(RoomEvent.TrackUnsubscribed, (_track: RemoteTrack, publication: RemoteTrackPublication) => {
            setRemoteTracks((prev) => prev.filter((track) => track.trackPublication.trackSid !== publication.trackSid));
        });

        try {
            // Get a token from your application server with the room name and participant name
            const token = await getToken();

            // Connect to the room with the LiveKit URL and the token
            await room.connect(LIVEKIT_URL, token);


            // Publish your camera and microphone
            await room.localParticipant.enableCameraAndMicrophone();
            const videoTrackPublication = room.localParticipant.videoTrackPublications.values().next().value;
            if (videoTrackPublication) {
                setLocalTrack(videoTrackPublication.videoTrack);
            }
        } catch (error) {
            console.log("There was an error connecting to the room:", (error as Error).message);
            await leaveRoom();
        }
    }

    async function leaveRoom() {
        // Leave the room by calling 'disconnect' method over the Room object
        await room?.disconnect();

        // Reset the state
        setRoom(undefined);
        setLocalTrack(undefined);
        setRemoteTracks([]);
    }

    /**
     * --------------------------------------------
     * GETTING A TOKEN FROM YOUR APPLICATION SERVER
     * --------------------------------------------
     * The method below request the creation of a token to
     * your application server. This prevents the need to expose
     * your LiveKit API key and secret to the client side.
     *
     * In this sample code, there is no user control at all. Anybody could
     * access your application server endpoints. In a real production
     * environment, your application server must identify the user to allow
     * access to the endpoints.
     */
    async function getToken() {
        // const response = await fetch(APPLICATION_SERVER_URL + "token", {
        //     method: "POST",
        //     headers: {
        //         "Content-Type": "application/json"
        //     },
        //     body: JSON.stringify({
        //         roomName: roomName,
        //         participantName: participantName
        //     })
        // });

        // if (!response.ok) {
        //     const error = await response.json();
        //     throw new Error(`Failed to get token: ${error.errorMessage}`);
        // }

        // const data = await response.json();
        // return data.token;
        if (participantName==="participant_name" && roomName==="room_name") {
            return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ2aWRlbyI6eyJyb29tSm9pbiI6dHJ1ZSwicm9vbSI6InJvb21fbmFtZSIsImNhblB1Ymxpc2giOnRydWUsImNhblN1YnNjcmliZSI6dHJ1ZSwiY2FuUHVibGlzaERhdGEiOnRydWV9LCJzdWIiOiJwYXJ0aWNpcGFudF9uYW1lIiwiaXNzIjoiZGV2a2V5IiwibmJmIjoxNzQ4OTI3NDU2LCJleHAiOjE3NDg5NDkwNTZ9.e9pGShfa4dqXlfDV31ACAXzNe-olUJj2bN560yiE7f0";
        }
        else if (participantName==="participant_name1" && roomName==="room_name") {
            return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ2aWRlbyI6eyJyb29tSm9pbiI6dHJ1ZSwicm9vbSI6InJvb21fbmFtZSIsImNhblB1Ymxpc2giOnRydWUsImNhblN1YnNjcmliZSI6dHJ1ZSwiY2FuUHVibGlzaERhdGEiOnRydWV9LCJzdWIiOiJwYXJ0aWNpcGFudF9uYW1lMSIsImlzcyI6ImRldmtleSIsIm5iZiI6MTc0ODk0OTkyMywiZXhwIjoxNzQ4OTcxNTIzfQ.89KNx4-mHnIkZUx95SRW6iakhXz1jMXAEXcIKuq-1j8";
        }
        else if (participantName==="participant_name2" && roomName==="room_name") {
            return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ2aWRlbyI6eyJyb29tSm9pbiI6dHJ1ZSwicm9vbSI6InJvb21fbmFtZSIsImNhblB1Ymxpc2giOnRydWUsImNhblN1YnNjcmliZSI6dHJ1ZSwiY2FuUHVibGlzaERhdGEiOnRydWV9LCJzdWIiOiJwYXJ0aWNpcGFudF9uYW1lMiIsImlzcyI6ImRldmtleSIsIm5iZiI6MTc0ODk0OTk3NiwiZXhwIjoxNzQ4OTcxNTc2fQ.o1xIY1g-rxYvFJanywy_2mRmyr99mw5pVSlwa7hOZLk";
        }
        else if (participantName==="participant_name3" && roomName==="room_name") {
            return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ2aWRlbyI6eyJyb29tSm9pbiI6dHJ1ZSwicm9vbSI6InJvb21fbmFtZSIsImNhblB1Ymxpc2giOnRydWUsImNhblN1YnNjcmliZSI6dHJ1ZSwiY2FuUHVibGlzaERhdGEiOnRydWV9LCJzdWIiOiJwYXJ0aWNpcGFudF9uYW1lMyIsImlzcyI6ImRldmtleSIsIm5iZiI6MTc0ODk0OTk3NiwiZXhwIjoxNzQ4OTcxNTc2fQ.8ouk5hT43mJLj9xfy7z0ANUtyhDlFd8wrYZBfbH_teQ";
        }
        else if (participantName==="participant_name4" && roomName==="room_name") {
            return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ2aWRlbyI6eyJyb29tSm9pbiI6dHJ1ZSwicm9vbSI6InJvb21fbmFtZSIsImNhblB1Ymxpc2giOnRydWUsImNhblN1YnNjcmliZSI6dHJ1ZSwiY2FuUHVibGlzaERhdGEiOnRydWV9LCJzdWIiOiJwYXJ0aWNpcGFudF9uYW1lNCIsImlzcyI6ImRldmtleSIsIm5iZiI6MTc0ODk0OTk3NiwiZXhwIjoxNzQ4OTcxNTc2fQ.NxvdxgPkTxXLbb7QlyabOiubILz5Y-qQB8iJs2SAl5A";
        }
        else if (participantName==="participant_name5" && roomName==="room_name") {
            return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ2aWRlbyI6eyJyb29tSm9pbiI6dHJ1ZSwicm9vbSI6InJvb21fbmFtZSIsImNhblB1Ymxpc2giOnRydWUsImNhblN1YnNjcmliZSI6dHJ1ZSwiY2FuUHVibGlzaERhdGEiOnRydWV9LCJzdWIiOiJwYXJ0aWNpcGFudF9uYW1lNSIsImlzcyI6ImRldmtleSIsIm5iZiI6MTc0ODk0OTk3NiwiZXhwIjoxNzQ4OTcxNTc2fQ.SmUSnRd3wTQhvcghPvvmiiVcvJAQUFsaVpn2X060zys";
        }
        else if (participantName==="participant_name6" && roomName==="room_name") {
            return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ2aWRlbyI6eyJyb29tSm9pbiI6dHJ1ZSwicm9vbSI6InJvb21fbmFtZSIsImNhblB1Ymxpc2giOnRydWUsImNhblN1YnNjcmliZSI6dHJ1ZSwiY2FuUHVibGlzaERhdGEiOnRydWV9LCJzdWIiOiJwYXJ0aWNpcGFudF9uYW1lNiIsImlzcyI6ImRldmtleSIsIm5iZiI6MTc0ODk0OTk3NiwiZXhwIjoxNzQ4OTcxNTc2fQ.XPCAP2Ar0d8iwGrbUzYwupeIXj6SXKFIRXFLz1A1D0Y";
        }
        else if (participantName==="participant_name7" && roomName==="room_name") {
            return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ2aWRlbyI6eyJyb29tSm9pbiI6dHJ1ZSwicm9vbSI6InJvb21fbmFtZSIsImNhblB1Ymxpc2giOnRydWUsImNhblN1YnNjcmliZSI6dHJ1ZSwiY2FuUHVibGlzaERhdGEiOnRydWV9LCJzdWIiOiJwYXJ0aWNpcGFudF9uYW1lNyIsImlzcyI6ImRldmtleSIsIm5iZiI6MTc0ODk0OTk3NiwiZXhwIjoxNzQ4OTcxNTc2fQ.ELfszouwouy00jEEm9dpBP4dbzV8dyStcdG0TPwyU9A";
        }
        return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ2aWRlbyI6eyJyb29tSm9pbiI6dHJ1ZSwicm9vbSI6InJvb21fbmFtZSIsImNhblB1Ymxpc2giOnRydWUsImNhblN1YnNjcmliZSI6dHJ1ZSwiY2FuUHVibGlzaERhdGEiOnRydWV9LCJzdWIiOiJwYXJ0aWNpcGFudF9uYW1lIiwiaXNzIjoiZGV2a2V5IiwibmJmIjoxNzQ4OTI3NDU2LCJleHAiOjE3NDg5NDkwNTZ9.e9pGShfa4dqXlfDV31ACAXzNe-olUJj2bN560yiE7f0";

    }

    return (
        <>
            {!room ? (
                <div id="join">
                    <div id="join-dialog">
                        <h2>Join a Video Room</h2>
                        <form
                            onSubmit={(e) => {
                                joinRoom();
                                e.preventDefault();
                            }}
                        >
                            <div>
                                <label htmlFor="participant-name">Participant</label>
                                <input
                                    id="participant-name"
                                    className="form-control"
                                    type="text"
                                    value={participantName}
                                    onChange={(e) => setParticipantName(e.target.value)}
                                    required
                                />
                            </div>
                            <div>
                                <label htmlFor="room-name">Room</label>
                                <input
                                    id="room-name"
                                    className="form-control"
                                    type="text"
                                    value={roomName}
                                    onChange={(e) => setRoomName(e.target.value)}
                                    required
                                />
                            </div>
                            <button
                                className="btn btn-lg btn-success"
                                type="submit"
                                disabled={!roomName || !participantName}
                            >
                                Join!
                            </button>
                        </form>
                    </div>
                </div>
            ) : (
                <div id="room">
                    <div id="room-header">
                        <h2 id="room-title">{roomName}</h2>
                        <button className="btn btn-danger" id="leave-room-button" onClick={leaveRoom}>
                            Leave Room
                        </button>
                    </div>
                    <div id="layout-container">
                        {localTrack && (
                            <VideoComponent track={localTrack} participantIdentity={participantName} local={true} />
                        )}
                        {remoteTracks.map((remoteTrack) =>
                            remoteTrack.trackPublication.kind === "video" ? (
                                <VideoComponent
                                    key={remoteTrack.trackPublication.trackSid}
                                    track={remoteTrack.trackPublication.videoTrack!}
                                    participantIdentity={remoteTrack.participantIdentity}
                                />
                            ) : (
                                <AudioComponent
                                    key={remoteTrack.trackPublication.trackSid}
                                    track={remoteTrack.trackPublication.audioTrack!}
                                />
                            )
                        )}
                    </div>
                </div>
            )}
        </>
    );
}

export default App;
