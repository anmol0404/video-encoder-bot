import json
import os
import datetime
import asyncio

class Database:
    def __init__(self, uri, database_name):
        self.db_dir = "data"
        self.db_file = os.path.join(self.db_dir, "database.json")
        if not os.path.exists(self.db_dir):
            os.makedirs(self.db_dir)
            
        self.data = {
            "users": {},
            "status": {}
        }
        self.load_db()

    def load_db(self):
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    self.data = json.load(f)
            except Exception as e:
                print(f"Error loading database: {e}")
        else:
            self.save_db()

    def save_db(self):
        try:
            with open(self.db_file, 'w') as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"Error saving database: {e}")

    def new_user(self, id):
        return dict(
            id=id,
            join_date=datetime.date.today().isoformat(),
            extensions='MKV',
            hevc=False,
            aspect=False,
            cabac=False,
            reframe='pass',
            tune=True,
            frame='source',
            audio='aac',
            sample='source',
            bitrate='128',
            bits=False,
            channels='source',
            drive=False,
            metadata=True,
            hardsub=False,
            watermark=False,
            subtitles=True,
            resolution='480',
            upload_as_doc=False,
            crf=24,
            preset='f',
            resize=False,
            interactive_mode=True
        )

    async def add_user(self, id):
        user = self.new_user(id)
        self.data["users"][str(id)] = user
        self.save_db()

    async def is_user_exist(self, id):
        return str(id) in self.data["users"]

    async def total_users_count(self):
        return len(self.data["users"])

    async def get_all_users(self):
        # Simulate cursor with a list for compatibility if needed, 
        # but the original code iterates over it. 
        # The original code used `self.col.find({})` which returns a cursor.
        # We'll need to check consumption. If it's awaited or iterated asynchronously, 
        # a list might work if the caller handles it, or we might need an async generator.
        # Most simple implementation: return list of values
        return list(self.data["users"].values())

    async def reset_user(self, id):
        if str(id) in self.data["users"]:
            self.data["users"][str(id)] = self.new_user(id)
            self.save_db()

    async def delete_user(self, user_id):
        if str(user_id) in self.data["users"]:
            del self.data["users"][str(user_id)]
            self.save_db()

    # Telegram Related

    # Upload As Doc
    async def set_upload_as_doc(self, id, upload_as_doc):
        if str(id) in self.data["users"]:
            self.data["users"][str(id)]['upload_as_doc'] = upload_as_doc
            self.save_db()

    async def get_upload_as_doc(self, id):
        user = self.data["users"].get(str(id))
        return user.get('upload_as_doc', False) if user else False

    # Encoding Settings

    # Resize
    async def set_resize(self, id, resize):
        if str(id) in self.data["users"]:
            self.data["users"][str(id)]['resize'] = resize
            self.save_db()

    async def get_resize(self, id):
        user = self.data["users"].get(str(id))
        return user.get('resize', 'resize') if user else 'resize'

    # Frame
    async def set_frame(self, id, frame):
        if str(id) in self.data["users"]:
            self.data["users"][str(id)]['frame'] = frame
            self.save_db()

    async def get_frame(self, id):
        user = self.data["users"].get(str(id))
        return user.get('frame', 'source') if user else 'source'

    # Convert To 720p
    async def set_resolution(self, id, resolution):
        if str(id) in self.data["users"]:
            self.data["users"][str(id)]['resolution'] = resolution
            self.save_db()

    async def get_resolution(self, id):
        user = self.data["users"].get(str(id))
        return user.get('resolution', '480') if user else '480'

    # Video Bits
    async def set_bits(self, id, bits):
        if str(id) in self.data["users"]:
            self.data["users"][str(id)]['bits'] = bits
            self.save_db()

    async def get_bits(self, id):
        user = self.data["users"].get(str(id))
        return user.get('bits', False) if user else False

    # Copy Subtitles
    async def set_subtitles(self, id, subtitles):
        if str(id) in self.data["users"]:
            self.data["users"][str(id)]['subtitles'] = subtitles
            self.save_db()

    async def get_subtitles(self, id):
        user = self.data["users"].get(str(id))
        return user.get('subtitles', False) if user else False

    # Sample rate
    async def set_samplerate(self, id, sample):
        if str(id) in self.data["users"]:
            self.data["users"][str(id)]['sample'] = sample
            self.save_db()

    async def get_samplerate(self, id):
        user = self.data["users"].get(str(id))
        return user.get('sample', '44.1K') if user else '44.1K'

    # Extensions
    async def set_extensions(self, id, extensions):
        if str(id) in self.data["users"]:
            self.data["users"][str(id)]['extensions'] = extensions
            self.save_db()

    async def get_extensions(self, id):
        user = self.data["users"].get(str(id))
        return user.get('extensions', 'MP4') if user else 'MP4'

    # Bit rate
    async def set_bitrate(self, id, bitrate):
        if str(id) in self.data["users"]:
            self.data["users"][str(id)]['bitrate'] = bitrate
            self.save_db()

    async def get_bitrate(self, id):
        user = self.data["users"].get(str(id))
        return user.get('bitrate', '128') if user else '128'

    # Reframe
    async def set_reframe(self, id, reframe):
        if str(id) in self.data["users"]:
            self.data["users"][str(id)]['reframe'] = reframe
            self.save_db()

    async def get_reframe(self, id):
        user = self.data["users"].get(str(id))
        return user.get('reframe', 'pass') if user else 'pass'

    # Audio Codec
    async def set_audio(self, id, audio):
        if str(id) in self.data["users"]:
            self.data["users"][str(id)]['audio'] = audio
            self.save_db()

    async def get_audio(self, id):
        user = self.data["users"].get(str(id))
        return user.get('audio', 'dd') if user else 'dd'

    # Audio Channels
    async def set_channels(self, id, channels):
        if str(id) in self.data["users"]:
            self.data["users"][str(id)]['channels'] = channels
            self.save_db()

    async def get_channels(self, id):
        user = self.data["users"].get(str(id))
        return user.get('channels', 'source') if user else 'source'

    # Metadata Watermark
    async def set_metadata_w(self, id, metadata):
        if str(id) in self.data["users"]:
            self.data["users"][str(id)]['metadata'] = metadata
            self.save_db()

    async def get_metadata_w(self, id):
        user = self.data["users"].get(str(id))
        return user.get('metadata', False) if user else False

    # Watermark
    async def set_watermark(self, id, watermark):
        if str(id) in self.data["users"]:
            self.data["users"][str(id)]['watermark'] = watermark
            self.save_db()

    async def get_watermark(self, id):
        user = self.data["users"].get(str(id))
        return user.get('watermark', False) if user else False

    # Preset
    async def set_preset(self, id, preset):
        if str(id) in self.data["users"]:
            self.data["users"][str(id)]['preset'] = preset
            self.save_db()

    async def get_preset(self, id):
        user = self.data["users"].get(str(id))
        return user.get('preset', 'uf') if user else 'uf'

    # Hard Sub
    async def set_hardsub(self, id, hardsub):
        if str(id) in self.data["users"]:
            self.data["users"][str(id)]['hardsub'] = hardsub
            self.save_db()

    async def get_hardsub(self, id):
        user = self.data["users"].get(str(id))
        return user.get('hardsub', False) if user else False

    # HEVC
    async def set_hevc(self, id, hevc):
        if str(id) in self.data["users"]:
            self.data["users"][str(id)]['hevc'] = hevc
            self.save_db()

    async def get_hevc(self, id):
        user = self.data["users"].get(str(id))
        return user.get('hevc', False) if user else False

    # Tune
    async def set_tune(self, id, tune):
        if str(id) in self.data["users"]:
            self.data["users"][str(id)]['tune'] = tune
            self.save_db()

    async def get_tune(self, id):
        user = self.data["users"].get(str(id))
        return user.get('tune', False) if user else False

    # CABAC
    async def set_cabac(self, id, cabac):
        if str(id) in self.data["users"]:
            self.data["users"][str(id)]['cabac'] = cabac
            self.save_db()

    async def get_cabac(self, id):
        user = self.data["users"].get(str(id))
        return user.get('cabac', False) if user else False

    # Aspect ratio
    async def set_aspect(self, id, aspect):
        if str(id) in self.data["users"]:
            self.data["users"][str(id)]['aspect'] = aspect
            self.save_db()

    async def get_aspect(self, id):
        user = self.data["users"].get(str(id))
        return user.get('aspect', False) if user else False

    # Google Drive
    async def set_drive(self, id, drive):
        if str(id) in self.data["users"]:
            self.data["users"][str(id)]['drive'] = drive
            self.save_db()

    async def get_drive(self, id):
        user = self.data["users"].get(str(id))
        return user.get('drive', False) if user else False

    # CRF
    async def get_crf(self, id):
        user = self.data["users"].get(str(id))
        return user.get('crf', 24) if user else 24

    async def set_crf(self, id, crf):
        if str(id) in self.data["users"]:
            self.data["users"][str(id)]['crf'] = crf
            self.save_db()

    # Process killed status
    async def get_killed_status(self):
        status = self.data["status"].get('killed')
        if not status:
            self.data["status"]['killed'] = {'id': 'killed', 'status': False}
            self.save_db()
            return False
        else:
            return status.get('status')

    async def set_killed_status(self, status):
        if 'killed' not in self.data["status"]:
            self.data["status"]['killed'] = {'id': 'killed'}
        self.data["status"]['killed']['status'] = status
        self.save_db()

    # Auth Chat
    async def get_chat(self):
        status = self.data["status"].get('auth')
        if not status:
            self.data["status"]['auth'] = {'id': 'auth', 'chat': '5217257368'}
            self.save_db()
            return '5217257368'
        else:
            return status.get('chat')

    async def set_chat(self, chat):
        if 'auth' not in self.data["status"]:
            self.data["status"]['auth'] = {'id': 'auth'}
        self.data["status"]['auth']['chat'] = chat
        self.save_db()

    # Auth Sudo
    async def get_sudo(self):
        status = self.data["status"].get('sudo')
        if not status:
            self.data["status"]['sudo'] = {'id': 'sudo', 'sudo_': '5217257368'}
            self.save_db()
            return '5217257368'
        else:
            return status.get('sudo_')

        self.data["status"]['sudo']['sudo_'] = sudo
        self.save_db()

    # Interactive Mode
    async def set_interactive_mode(self, id, interactive_mode):
        if str(id) in self.data["users"]:
            self.data["users"][str(id)]['interactive_mode'] = interactive_mode
            self.save_db()

    async def get_interactive_mode(self, id):
        user = self.data["users"].get(str(id))
        return user.get('interactive_mode', True) if user else True

