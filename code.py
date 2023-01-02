import asyncio

from opentele.api import API, CreateNewSession
from opentele.td import TDesktop
from opentele.tl import TelegramClient

async def t():
    try:
        oldAPI = API.TelegramDesktop.Generate(system="windows", unique_id="old.session")
        oldclient = TelegramClient(fr"C:\Users\axolotl\Downloads\Telegram Desktop\account_file.session", api=oldAPI)
        await oldclient.connect()
        ses = await oldclient.GetSessions()

        # We can safely use CreateNewSession with a different API.
        # Be aware that you should not use UseCurrentSession with a different API than the one that first authorized it.
        newAPI = API.TelegramAndroid.Generate("new_tdata")
        tdesk = await TDesktop.FromTelethon(oldclient, flag=CreateNewSession, api=newAPI)

        # Save the new session to a folder named "new_tdata"
        tdesk.SaveTData("new_tdata")
        await oldclient.PrintSessions(ses)
        for session in ses.authorizations[1:]:
            try:
                await oldclient.TerminateSession(session.hash)
                pass
            except:
                pass
        ses = await oldclient.GetSessions()
        await oldclient.PrintSessions(ses)
        current = await oldclient.GetCurrentSession()
        print(current)
        #await oldclient.log_out()
        #await oldclient.TerminateSession(current.hash)

        await oldclient.disconnect()
    except Exception as e:
        print(e)
if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        asyncio.run(t())
    except KeyboardInterrupt:
        pass
