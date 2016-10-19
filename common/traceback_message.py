import inspect
import datetime
import time
import traceback





class TracebackError:

    @staticmethod
    def traceback_error(stack):
        calling_function = inspect.stack()[1][3]
        error_traceback = traceback.format_exc()
        class_called = str(stack[1][0].f_locals["self"].__class__)
        ts = time.time()
        time_stamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        time_stamped_traceback_message = ("  The class, *" + str(class_called) + "* and method *" + calling_function + "* were called at *" + time_stamp + "*" + "\n" + error_traceback)
        return (time_stamped_traceback_message)

