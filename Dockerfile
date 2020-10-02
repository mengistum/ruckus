# Use CentOS Container to build your container for Network automation
FROM centos

# Install "yum database update", python38, and NORNIR module
RUN yum -y update && yum install -y python38 && python3 -m pip install requests

# Copy scripts and necessary files to /src folder
COPY . /src/ruckus/

# Run bash
CMD ["/bin/bash"]