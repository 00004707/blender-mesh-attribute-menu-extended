# Logger object
# LOGGER = None

# Addon log, elements format: {'level': level.name, 'message': message, 'timestamp': time.time(), 'who': obj reference})
LOG = []

# Snapshot of a log at given moment, used by crash hander UI to not overwrite log with new values
LOG_SNAPSHOT = []



def make_log_snapshot():
    """Copies current log into a new container so it does not get overwritten

    Returns:
        None
    """

    global LOG, LOG_SNAPSHOT
    LOG_SNAPSHOT = LOG.copy()

    # for mod in addon_utils.modules():
    #     if mod.bl_info['name'] == BL_INFO['name']:
    #         __addon_self_module__ = mod
    #         return

# Fake operators
# ------------------------------

# Utility operators
# -----------------------------

# ------------------------------------------
# Preferences

# Generic UI elements
# ------------------------------------------ 

 # Generic datatypes

# Logging
# -----------------------------
# Might be useful for debugging
    
class ELogLevel(Enum):
    SUPER_VERBOSE = 0
    VERBOSE = 1
    INFO = 2
    WARNING = 3
    ERROR = 4

def init_logging():
    global LOGGER
    #LOGGER = logging.getLogger(__addon_package_name__)
    #LOGGER.setLevel(logging.DEBUG)

def get_logger():
    global LOGGER
    if not LOGGER:
        init_logging()
    return LOGGER

def is_full_logging_enabled():
    """
    Some logging operations can slow down things drastically, can be enabled if needed
    """
    return get_preferences_attrib('en_slow_logging_ops') or get_preferences_attrib('console_loglevel') == 0

def log(who, message:str, level:ELogLevel):
    """
    Logs to internal set and optionally to system console
    """

    if hasattr(who, '__name__'):
        who = who.__name__
    else:
        who = "Unknown"
    
    console_message = f"[{str(time.time()).ljust(20)[-16:]}][{str(level.name)[:4]}][{who.ljust(16)[:16]}]: {message}"
    
    # if level == ELogLevel.VERBOSE or level == ELogLevel.SUPER_VERBOSE:
    #     get_logger().debug("[MAME]" + message)
    # elif level == ELogLevel.INFO:
    #     get_logger().info("[MAME]" + message)
    # elif level == ELogLevel.WARNING:
    #     get_logger().warning("[MAME]" + message)
    # elif level == ELogLevel.ERROR:
    #     get_logger().error("[MAME]" + message)
    if level.value >= get_preferences_attrib("console_loglevel"):
        print("[MAME]" + console_message)

    global LOG

    LOG.append({'level': level.name, 'message': message, 'timestamp': time.time(), 'who': who})
    while len(LOG) > get_preferences_attrib("max_log_lines"):
        LOG.pop()

class WINDOW_MANAGER_OT_mame_save_log_file(bpy.types.Operator, ExportHelper):
    """
    Saves log to a text file
    """

    bl_idname = "window_manager.mame_save_log_file"
    bl_label = "Save log file"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    # Filename
    filename_ext = ".txt"

    # File filter, i guess just to show less stuff in filepath selector
    filter_glob: bpy.props.StringProperty(
        default="*.txt",
        options={'HIDDEN'},
        maxlen=255,  
    )
    
    # File path
    filepath: bpy.props.StringProperty(
        name="File Path",
        description="Filepath used for exporting the file",
        maxlen=1024,
        subtype='FILE_PATH',
        default= "mame_log"
    )

    # Overwrite protection
    check_existing: bpy.props.BoolProperty(
        name="Check Existing",
        description="Check and warn on overwriting existing files",
        default=True,
        options={'HIDDEN'},
    )

    # Included info list
    included_info = [
        "Blender Version",
        "Addon version",
        "Time and date",
        "Last addon operations",
        "Last addon handled exceptions",
        "This addon preferences",
        "May contain user name"
    ]

    #Uses last captured log snapshot instead of live capture
    b_use_log_snapshot: bpy.props.BoolProperty(
        name="Use Log Snapshot",
        description="Uses last captured log snapshot instead of live capture",
        default=False,
    )

    # Generic error message
    err_msg_troubleshoot = "Check:\n"\
        "* if your user account has permissions to write to this file in specified location\n"\
        "* or if other program is using the specified file"

    @classmethod
    def poll(self, context):
        
        return True
    
    def execute(self, context):
        global LOG
        global BL_INFO
        
        # Try to open file for writing
        file = None
        try:
            file = open(self.filepath, "w")
        except Exception as exc:
            if file is not None:
                try:
                    file.close()
                except Exception:
                    pass
            bpy.ops.window_manager.mame_message_box(message="Failed to create log file.\n" + self.err_msg_troubleshoot
                                                    + f"\n More info:\n{str(exc)}", width=500)
            return {'CANCELLED'}
            
        # Prepare text file
        try:
            log_text = ""

            log_text += "Mesh Attributes Extended Addon Log File\n"
            log_text += f"Version { bl_version_tuple_to_friendly_string(get_bl_info_key_value('version')) }\n"
            log_text += f"Blender version: {bpy.app.version_string}\n"
            date_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            log_text += f"Creation Time: {date_time}\n"

            log_text += f"-----------------------\n"
            log_text += f"Log Entries\n"
            log_text += f"-----------------------\n"
            
            for i, log_el in enumerate(LOG):
                try:
                    
                    logline_temp = f"[{str(i).ljust(3)[:3]}]"\
                        f"[{str(log_el['timestamp']).ljust(16)[:16]}]"\
                        f"[{str(log_el['level'])[:4]}]"\
                        f"[{log_el['who'].ljust(16)[:16]}]:"\
                            f" {str(log_el['message'])}\n"
                    
                    # Anonymize paths
                    try:
                        username = os.getenv('username')
                        if username is not None:
                            logline_temp = logline_temp.replace(f"\\{username}\\", "\\ANONYMOUS_MAME_USER\\")
                    except Exception:
                        pass
                    log_text += logline_temp
                except Exception as exc:
                    log_text += f"Failed to write {str(i)} log element - {str(exc)}\n"
                
            log_text += f"-----------------------\n"
            log_text += f"Preferences\n"
            log_text += f"-----------------------\n"
            try:
                # Get preferences panel values
                prefs = bpy.context.preferences.addons[__addon_package_name__].preferences
                excluded_pref_attrs = ['bl_rna', 'bl_idname', 'rna_type']
                pref_attr = [attr for attr in dir(prefs) if (attr not in excluded_pref_attrs
                                                            and not callable(getattr(prefs, attr)) 
                                                            and not attr.startswith("__"))]
                
                for i, a in enumerate(pref_attr):
                    try:
                        log_text += f"[{str(i)}] {a}: {get_preferences_attrib(a)}\n"
                    except Exception as exc:
                        log_text += f"Failed to write {str(i)} log element - {str(exc)}\n"
                    
            except Exception as exc:
                log_text += f"Failed to get preferences - {str(exc)}\n"
        
        except Exception as exc:
            if file is not None:
                file.close()
            call_catastrophic_crash_handler(WINDOW_MANAGER_OT_mame_save_log_file, exc)

        try:
            file.write(log_text)
        except Exception as exc:
            try:
                file.close()
            except Exception:
                pass
            bpy.ops.window_manager.mame_message_box(message="Failed to write log to log file.\n" 
                                                    + self.err_msg_troubleshoot + f"\n More info:\n{str(exc)}", width=500)
            return {'CANCELLED'}
        
        # Close file
        try:
            file.close()
        except Exception:
            pass

        return {'FINISHED'}
    
    def invoke(self, context, _event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        header_box = col.box()
        header_box.label(text="Included information in a log file", icon='INFO')

        for el in self.included_info:
            row = col.row(align=True)
            row.label(text='', icon='DOT')
            row.label(text=el)

class CrashMessageBox(bpy.types.Operator):
    """
    Shows a crash message box + save log to file
    """
    bl_idname = "window_manager.mame_crash_handler"
    bl_label = "Mesh Attributes Menu Extended - Crash!"
    bl_options = {'REGISTER', 'INTERNAL'}

    # trick to make the dialog box open once and not again after pressing ok
    times = 0

    b_show_details: bpy.props.BoolProperty(name="Show details", description="Shows details of an exception", default = False)

    def execute(self, context):
        self.times += 1
        if self.times < 2:
            return context.window_manager.invoke_props_dialog(self, width=800)
        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout

        # Grab info
        suspect_name = MAME_CRASH_HANDLER_WHO.__name__ if hasattr(MAME_CRASH_HANDLER_WHO, '__name__') else "Can't determine"
        try:
            cause = str(MAME_CRASH_HANDLER_WHAT_HAPPENED)
        except Exception:
            cause = "Unknown"
        try:
            details = str(MAME_CRASH_HANDLER_WHAT_HAPPENED)
        except Exception:
            details = "None"
        if  issubclass(type(MAME_CRASH_HANDLER_EXCEPTION), Exception):
            exc = MAME_CRASH_HANDLER_EXCEPTION
        else:
            exc = None
        
        # Show info
            
        box = layout.box()
        r = box.column()
        r.alert = True
        r.label(text="Oops! Addon has crashed", icon="ERROR")

        r = layout.row()
        r.operator_context = "INVOKE_DEFAULT"
        r.operator("window_manager.mame_save_log_file", text="Save Log File")
        r.operator("window_manager.mame_report_issue", text="Report Issue")

        r = layout.row()
        r.enabled = get_preferences_attrib("console_loglevel") > 1
        r.prop(self, 'b_show_details', toggle=True)
        if self.b_show_details or get_preferences_attrib("console_loglevel") < 2:
            box = layout.box()
            r = box.column()
            r.label(text=f"Caused by", icon="CANCEL")
            r.label(text=f"{suspect_name}")
            box = layout.box()

            r = box.column()
            r.label(text=f"Exception Type", icon="QUESTION")
            try:
                r.label(text=f"{repr(exc) if exc else 'Not available'}")
            except Exception:
                r.label(text=f"{'Unknown'}")
            box = layout.box()
            r = box.column()
            r.label(text=f"Traceback", icon="FILE_TEXT")
            for line in MAME_CRASH_HANDLER_EXCEPTION_STR.splitlines():
                r.label(text=line)
        
class ShowLog(bpy.types.Operator):
    """
    Shows MAME log
    """
    bl_idname = "window_manager.mame_show_log"
    bl_label = "Mesh Attributes Menu Extended - Log"
    bl_options = {'REGISTER', 'INTERNAL'}

    # trick to make the dialog box open once and not again after pressing ok
    times = 0

    def execute(self, context):
        self.times += 1
        if self.times < 2:
            return context.window_manager.invoke_props_dialog(self, width=800)
        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout
        global LOG
        r = layout.row()
        r.label(text=f"Log elements: {str(len(LOG))}, max count {str(get_preferences_attrib('max_log_lines'))}")

        for i, el in enumerate(LOG):
            alert = False
            if el['level'] == 'VERBOSE':
                icon = 'ALIGN_JUSTIFY'
            elif el['level'] == 'SUPER_VERBOSE':
                icon = 'ALIGN_FLUSH'
            elif el['level'] == 'WARNING':
                icon = 'ERROR'
                alert = True
            elif el['level'] == 'ERROR':
                icon = 'CANCEL'
                alert = True
            else:
                icon = 'INFO'
            layout.alert = alert
            r = layout.row()
            r.label(text=f"{el['message']}", icon=icon)
            

        layout.alert = False
        r = layout.row()
        r.operator("window_manager.mame_clear_log")
        
class ClearLog(bpy.types.Operator):
    """
    Clears MAME log
    """
    bl_idname = "window_manager.mame_clear_log"
    bl_label = "Clear Log"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        global LOG
        LOG.clear()
        log(ClearLog, "Log cleared", ELogLevel.INFO)
        return {'FINISHED'}

# Catastrophic Error Handling
# -----------------------------
# Crash gracefully and tell the user what went wrong instead of cryptic python stuff
        
def call_catastrophic_crash_handler(who, exception:Exception):
    """
    If something went wrong
    In front of your screen
    Who you gonna call?
    CRASH HANDLER
    """
    
    # there is probably more sophiscated way to do this, but guess what, it's the simplest one and working
    global MAME_CRASH_HANDLER_WHO
    MAME_CRASH_HANDLER_WHO = who
    global MAME_CRASH_HANDLER_EXCEPTION
    MAME_CRASH_HANDLER_EXCEPTION = exception
    global MAME_CRASH_HANDLER_EXCEPTION_STR
    MAME_CRASH_HANDLER_EXCEPTION_STR = format_exc()

    
    log(str(who), MAME_CRASH_HANDLER_EXCEPTION_STR, ELogLevel.ERROR)
    
    # Create log snapshot so it won't get overwritten by new entries
    make_log_snapshot()

    # Show stuff to console
    print(MAME_CRASH_HANDLER_EXCEPTION_STR)

    # Show UI
    bpy.ops.window_manager.mame_crash_handler()

MAME_CRASH_HANDLER_WHO = None
MAME_CRASH_HANDLER_EXCEPTION:Exception = None
MAME_CRASH_HANDLER_EXCEPTION_STR:str = ''


class CrashMessageBox(bpy.types.Operator):
    """
    Shows a crash message box + save log to file
    """
    bl_idname = "window_manager.mame_crash_handler"
    bl_label = "Mesh Attributes Menu Extended - Crash!"
    bl_options = {'REGISTER', 'INTERNAL'}

    # trick to make the dialog box open once and not again after pressing ok
    times = 0

    b_show_details: bpy.props.BoolProperty(name="Show details", description="Shows details of an exception", default = False)

    def execute(self, context):
        self.times += 1
        if self.times < 2:
            return context.window_manager.invoke_props_dialog(self, width=800)
        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout

        # Grab info
        suspect_name = MAME_CRASH_HANDLER_WHO.__name__ if hasattr(MAME_CRASH_HANDLER_WHO, '__name__') else "Can't determine"
        if  issubclass(type(MAME_CRASH_HANDLER_EXCEPTION), Exception):
            exc = MAME_CRASH_HANDLER_EXCEPTION
        else:
            exc = None
        
        # Show info
            
        box = layout.box()
        r = box.column()
        r.alert = True
        r.label(text="Oops! Addon has crashed", icon="ERROR")
        
        r = layout.row()
        r.alert = True
        op = r.operator("window_manager.mame_save_log_file", text="Save Log")
        op.b_use_log_snapshot = True
        r.operator("window_manager.mame_report_issue", text="Report Issue")

        r = layout.row()
        r.enabled = get_preferences_attrib("console_loglevel") > 1
        r.prop(self, 'b_show_details', toggle=True)
        if self.b_show_details or get_preferences_attrib("console_loglevel") < 2:
            box = layout.box()
            r = box.column()
            r.label(text=f"Caused by", icon="CANCEL")
            r.label(text=f"{suspect_name}")
            box = layout.box()
            r = box.column()
            r.label(text=f"Exception Type", icon="QUESTION")
            try:
                r.label(text=f"{repr(exc) if exc else 'Not available'}")
            except Exception:
                r.label(text=f"{'Unknown'}")
            box = layout.box()
            r = box.column()
            r.label(text=f"Traceback", icon="FILE_TEXT")
            for line in MAME_CRASH_HANDLER_EXCEPTION_STR.splitlines():
                r.label(text=line)

