from controller import BittleX

# Manually specify the Bittle Bluetooth port
bittle = BittleX(selected_port='/dev/cu.BittleB3_SSP')

bittle.send_command('ksit')
bittle.send_command('kpu')
bittle.send_command('khi')

bittle.close()
