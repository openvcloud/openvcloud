@0x934efea7f327fff0;
struct CloudSpace {
  cloudSpaceId @0 :Text;
  accountId @1 :Text;
  machines @2 :List(VMachine);
  state @3 :Text;
  struct VMachine {
    id @0 :Text;
    type @1 :Text;
    vcpus @2 :Int8;
    cpuMinutes @3 :Float32;
    mem @4 :Float32;
    networks @5 :List(Nic);
    disks @6 :List(Disk);
    imageName @7 :Text;
    status @8 :Text;
    struct Nic {
      id @0 :Text;
      type @1 :Text;
      tx @2 :Float32;
      rx @3 :Float32;
    }
    struct Disk {
        id @0 :Text;
        size @1 :Float32;
        iopsRead  @2 :Float32;
        iopsWrite  @3 :Float32;
        iopsReadMax @4 :Float32;
        iopsWriteMax @5 :Float32;
    }
  }
}

struct Account {
  accountId @0  :UInt32;
  cloudspaces @1 :List(CloudSpace);
}
