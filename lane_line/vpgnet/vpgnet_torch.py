import torch
import torch.nn as nn

torch.manual_seed(294)


# 1	lane_solid_white
# 2	lane_broken_white
# 3	lane_double_white
# 4	lane_solid_yellow
# 5	lane_broken_yellow
# 6	lane_double_yellow

class VPGNet(nn.Module):

    def __init__(self):
        super(VPGNet, self).__init__()
        # Followed Figure 3 pg.5 of VPGNet paper
        self.shared = nn.Sequential(
            # Conv1
            nn.Conv2d(3, 96, kernel_size=8, stride=4, padding=0),  # changed to 8 from 11
            nn.MaxPool2d(kernel_size=3, stride=2),
            nn.LocalResponseNorm(96),
            # Conv2
            nn.Conv2d(96, 256, kernel_size=5, stride=1, padding=2),
            nn.MaxPool2d(kernel_size=3, stride=2),
            nn.LocalResponseNorm(256),
            # Conv3
            nn.Conv2d(256, 384, kernel_size=3, stride=1, padding=1),
            # Conv4
            nn.Conv2d(384, 384, kernel_size=3, stride=1, padding=1),
            # Conv5
            nn.Conv2d(384, 384, kernel_size=3, stride=1, padding=1),
            nn.MaxPool2d(kernel_size=3, stride=2),
            # Conv6
            nn.Conv2d(384, 4096, kernel_size=6, stride=1, padding=3),

        )
        # self.grid_box = Sequential(
        #     #Conv 7
        #     nn.Conv2d(4096, 4096, kernel_size=1, stride=1, padding=0), 
        #     nn.Dropout(),
        #     #Conv 8
        #     nn.Conv2d(4096, 256, kernel_size=1, stride=1, padding=0), 
        #     #Tiling
        #     nn.ConvTranspose2d(256, 4, kernel_size = 8)
        # )
        self.obj_mask = nn.Sequential(
            # Conv 7
            nn.ConvTranspose2d(4096, 384, kernel_size=2, stride=2),
            nn.Conv2d(384, 384, kernel_size=3, stride=1, padding=1),
            nn.ConvTranspose2d(384, 256, kernel_size=2, stride=2),
            nn.Conv2d(256, 256, kernel_size=3, stride=1, padding=1),
            nn.ConvTranspose2d(256, 3, kernel_size=2, stride=2),
        )
        self.vp = nn.Sequential(
            # Conv 7
            # nn.Conv2d(4096, 4096, kernel_size=1, stride=1, padding=0),
            # nn.Dropout(),
            # Conv 8
            nn.ConvTranspose2d(4096, 384, kernel_size=2, stride=2),
            nn.Conv2d(384, 384, kernel_size=3, stride=1, padding=1),
            nn.ConvTranspose2d(384, 256, kernel_size=2, stride=2),
            nn.Conv2d(256, 256, kernel_size=3, stride=1, padding=1),
            nn.ConvTranspose2d(256, 5, kernel_size=2, stride=2),
        )

    def forward(self, x):
        # Forward pass through shared layers
        x = self.shared(x)

        # Pass through the obj_mask branch
        obj_mask = torch.sigmoid(self.obj_mask(x))
        # #Reshape into (120,160,2)
        # obj_mask = obj_mask.view(-1,2,120,160)

        # Pass through the vp branch
        # vp = self.vp(x)
        vp = (torch.sigmoid(self.vp(x)))

        # print(vp.size())
        # #Reshape into (120,160,5)
        # vp = vp.view(-1,4,120,160)

        return obj_mask, vp
