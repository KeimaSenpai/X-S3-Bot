class Config(object):
      def __init__(self):
          self.BotToken     = '5252388096:AAH2vMvnXW_ROC8nVmdn8BRF_LKIXnftc5A'
          self.S3Token      = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2MjU1ODE0NTgsInVzZXJuYW1lIjoiNTM1OTYzNDI0NSIsInZlcnNpb24iOiIyMTgwOCJ9.gGLXlAyWlXG54SRtPLG5tvqAApDuoLMO2yJa3BLeJT0'
          self.ChunkSize    = 10
          self.ChunkFixed   = 150
          self.FileLimit    = 1024 * 1024 * 200
          self.ExcludeFiles = ['bot.py','Config.py','multiFile.py','toDus.py','requirements.txt','Procfile','__pycache__','.git','.profile.d','.heroku','bot.session','bot.session-journal','output','.tdb']
          self.ChunkedFileLimit = 1024 * 1024 * 1024
          self.InProcces = False
          self.BotChannel = '-1001792041368'
          self.AdminUsers = ['Keima_Senpai']
          self.current_user_msg = ''
          self.current_chanel_msg = ''
          self.procesing = False
          self.watching = False
          self.watch_message = []
          self.tokensdb = []
          self.tokenindex = 0


      def setS3Token(self,token : str):
          self.S3Token = token

      def setBotToken(self,token : str):
          self.BotToken = token

      def setChunkSize(self,chunk : int):
          self.ChunkSize = chunk

      def toStr(self):
          return '[Chunk Size]\n' + str(self.ChunkSize) + '\n\n[Token]\n' + self.S3Token

      def addToken(self,token):
          if token in self.tokensdb:
            print('Token eXist!')
          else:
               self.tokensdb.append(token)

      def stepTokenIndex(self):
          if (len(self.tokensdb) - 1) > self.tokenindex:
              self.tokenindex += 1
          else:
              self.tokenindex = 0

      def stepToken(self):
          if len(self.tokensdb) > 0:
              self.setS3Token(self.tokensdb[self.tokenindex])
          else:
              self.setS3Token('')
