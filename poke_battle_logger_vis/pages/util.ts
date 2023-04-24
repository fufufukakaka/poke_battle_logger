export const Auth0Domain = process.env.NEXT_PUBLIC_AUTH0_DOMAIN as string
export const Auto0ClientId = process.env.NEXT_PUBLIC_AUTH0_CLIENT_ID as string
export const ServerHost = process.env.NEXT_PUBLIC_BACKEND_HOST | 'http://127.0.0.1:8000'
export const ServerHostWebsocket = process.env.NEXT_PUBLIC_BACKEND_WEBSOCKET_HOST | 'ws://127.0.0.1:8000'
