# vagrant: добавить еще диск

```ruby
Vagrant.configure("2") do |config|

  MACHINES.each do |boxname, boxconfig|
    
    config.vm.define boxname do |box|

      # ...

      box.vm.provider :virtualbox do |vb|
        file_to_disk = 'disk2.vdi'
        unless File.exist?(file_to_disk)
            # 10 GB
            vb.customize ['createhd', '--filename', file_to_disk, '--size', 10 * 1024]
        end
        vb.customize ['storageattach', :id, '--storagectl', 'SATAController', '--port', 1, '--device', 0, '--type', 'hdd', '--medium', file_to_disk]

        # ...
      end

      # ...

    end
      
  end
    
end
  
```