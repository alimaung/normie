<html>
	<head>
		<style>
			.tabelLabel {
				font-size: 14px; font-family: 'Open Sans', Helvetica, sans-serif;"
			}
		</style>
	</head>
	<body style="background-color: #e8edf1; padding: 0; margin: 0;">
		<table width="100%" height="400" cellpadding="0" cellspacing="0"
			   style="margin: 0; padding: 0">
			<tr height="20">
				<td colspan="3"></td>
			</tr>
			<tr>
				<td width="10%"></td>
				<td width="80%" valign="top">
					<table style="background-color: #ffffff;" width="100%"
						   cellpadding="0" cellspacing="0">
						<tr height="15">
							<td colspan="3"></td>
						</tr>
						<tr>
							<td width="15"></td>
							<td valign="center"
								style="font-size: 16px; font-family: 'Open Sans', Helvetica, sans-serif; font-weight: bold;">
								Pinpoint Feedback Was Submitted</td>
							<td width="15"></td>
						</tr>
						<tr height="15">
							<td colspan="3"></td>
						</tr>
						<tr height="1" style="background-color: #e8edf1;">
							<td colspan="3"></td>
						</tr>
						<tr colspan="3" height="25">
							<td></td>
						</tr>

						<tr height="5"></tr>
						<tr>
							<td />
							<td>
								<table>
									<tr colspan="2">
										<td colspan="2">
											Submitted feedback for the
											<#if publicationName?has_content>
												${publicationName}
											<#else>
												(unknown Publication)
											</#if>
											for
											<#if revisionNumber?has_content>
												Revision ${revisionNumber}
											<#else>
												(unknown Revision)
											</#if>
										</td>
									</tr>
								</table>
							</td>
						</tr>
						<tr height="5"></tr>
						<tr height="1" style="background-color: #e8edf1;">
							<td colspan="3"></td>
						</tr>
						<tr>
							<td />
							<td>
								<table>
									<tr colspan="2">
										<td colspan="2" style="font-size: 14px; font-family: 'Open Sans', Helvetica, sans-serif; font-weight: bold;">
											With the below details:
										</td>
									</tr>
									</tr>
									<tr height="5"></tr>
									<tr>
										<td />
										<td>
											<table height="1" style="background-color: #e8edf1;">
												<#if userName?has_content>
													<tr colspan="2">
														<td colspan="2" class="tabelLabel">
															User Name
														</td>
														<td>:</td>
														<td colspan="2">
															${userName}
														</td>
													</tr>
												</#if>
												<tr colspan="2">
													<td colspan="2" class="tabelLabel">
														Publication Name
													</td>
													<td>:</td>
													<td colspan="2">
														<#if publicationName?has_content>
															${publicationName}
														<#else>
															(unknown Publication)
														</#if>
													</td>
												</tr>
												<#if documentRefKey?has_content || documentTitle?has_content>
													<tr colspan="2">
														<td colspan="2" class="tabelLabel">
															Data Module / Fragment Name
														</td>
														<td>:</td>
														<td colspan="2">
															<#if documentTitle?has_content>
																${documentTitle}
															</#if>
															<#if documentRefKey?has_content>
																${documentRefKey}
															</#if>
														</td>
													</tr>
												</#if>
												<#if feedbackText?has_content>
													<tr colspan="2">
														<td colspan="2" class="tabelLabel">
															Feedback Text
														</td>
														<td>:</td>
														<td colspan="2">
															${feedbackText}
														</td>
													</tr>
												</#if>
												<#if userEmail?has_content>
													<tr colspan="2">
														<td colspan="2" class="tabelLabel">
															User Email ID
														</td>
														<td>:</td>
														<td colspan="2">
															${userEmail}
														</td>
													</tr>
												</#if>
												<tr height="15">
													<td colspan="3"></td>
												</tr>
												<#if rr_feedback_sb_number?has_content>
													<tr colspan="2">
														<td colspan="2" class="tabelLabel">
															SB Number
														</td>
														<td>:</td>
														<td colspan="2">
															${rr_feedback_sb_number}
														</td>
													</tr>
												</#if>
												<#if rr_feedback_eng_serialnumber?has_content>
													<tr colspan="2">
														<td colspan="2" class="tabelLabel">
															Engine Serial Number
														</td>
														<td>:</td>
														<td colspan="2">
															${rr_feedback_eng_serialnumber}
														</td>
													</tr>
												</#if>
												<#if rr_feedback_amsn?has_content>
													<tr colspan="2">
														<td colspan="2" class="tabelLabel">
															Aircraft Manufacturers Serial Number
														</td>
														<td>:</td>
														<td colspan="2">
															${rr_feedback_amsn}
														</td>
													</tr>
												</#if>
												<#if rr_feedback_completion_date?has_content>
													<tr colspan="2">
														<td colspan="2" class="tabelLabel">
															Completion Date
														</td>
														<td>:</td>
														<td colspan="2">
															${rr_feedback_completion_date?date}
														</td>
													</tr>
												</#if>
											</table>
										</td>
									</tr>
									<tr height="15">
										<td colspan="3"></td>
									</tr>
									<tr height="1" style="background-color: #e8edf1;">
										<td colspan="3"></td>
									</tr>
									<tr height="15">
										<td colspan="3"></td>
									</tr>
									<tr height="25">
										<td colspan="3"></td>
									</tr>
								</table>
							</td>
							<td width="10%"></td>
						</tr>
					</table>
				</td>
			</tr>
		</table>
	</body>
</html>
