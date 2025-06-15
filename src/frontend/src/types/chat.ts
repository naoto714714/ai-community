export interface Message {
  id: string;
  channelId: string;
  userId: string;
  userName: string;
  content: string;
  timestamp: Date;
  isOwnMessage: boolean;
}

export interface Channel {
  id: string;
  name: string;
}
