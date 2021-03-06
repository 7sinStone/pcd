import multiprocessing
from subprocess import Popen, PIPE, check_output

from shinken.basemodule import BaseModule
from shinken.log import logger

properties = {
	'daemons' : ['arbiter'],
	'type' : 'pcd',
	'external' :True 
}


def job():
    str = ""
    err = ""
    try:
        logger.info('********** job method *********')
        p = Popen(['python', '/var/lib/shinken/modules/pcd/web_server/server.py'], stdout=PIPE, stderr=PIPE)
        p.communicate()
    except Exception as e:
        logger.info('job: ' + str(e))


def get_instance(plugin):
    logger.info('[PCD Module broker] YO !!!!!')
    instance = pcd_module_class(plugin)
    return instance



class pcd_module_class(BaseModule):
    def __init__(self, modconf):
        self.proc = None
        BaseModule.__init__(self, modconf)

    def init(self):
        logger.info('[PCD Module] init method')

    def hook_early_configuration(self, arb):
        try:
            logger.info('************** HOOK EARLY CONFIG CALLED **************')
            fh = open('/var/lib/shinken/modules/pcd/ipaddresses', 'w')
            for h in arb.conf.hosts:
                if not hasattr(h, 'address') and not hasattr(h, 'host_name'):
                    continue
                    addr = None
                # By default take the address, if not, take host_name
                if not hasattr(h, 'address'):
                    addr = h.host_name
                else:
                    addr = h.address
                fh.write(addr + '\n')
            fh.close()
        except Exception as e:
            logger.info('hook_early_config: ' + str(e))

    def main(self):
        try:
            proc = multiprocessing.Process(target=job)
            proc.start()
            proc.join()
        except Exception as e:
            logger.info('/////////////////////main: ' + str(e))

    def stop_process(self):
        logger.info('********* before leaving stop_process *********')
        try:
            server_pid = None
            ps = Popen(('ps', '-ef'), stdout=PIPE)
            output = check_output(('grep', '[s]erver.py'), stdin=ps.stdout)
            ps.wait()
            logger.info(output)
            server_pid = output.split()[1]
            if server_pid:
                logger.info('pid : ' + server_pid)
                Popen(('kill', '-9', server_pid), stdout=PIPE)
                ps.wait()
        except Exception as e:
            logger.info('stop_process: ' + str(e))
        super(pcd_module_class, self).stop_process()
