export interface Message {
  id: string;
  channelId: string;
  userId: string;
  userName: string;
  userType: 'user' | 'ai';
  content: string;
  timestamp: Date;
  isOwnMessage: boolean;
}

export interface Channel {
  id: string;
  name: string;
}

// バックエンドAPIレスポンス用の型定義
export interface MessageResponse {
  id: string;
  channelId: string;
  userId: string;
  userName: string;
  userType: 'user' | 'ai';
  content: string;
  timestamp: string;
  isOwnMessage: boolean;
}
